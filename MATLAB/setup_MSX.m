try 
d.unload
d.unloadMSX;
catch ERR
end 
fclose all;clear class;clear all;clc;close all;
addpath(genpath(pwd)); 
inpname = 'networks\CY-DBP_competition_stream_competition_6days.inp';
d = epanet(inpname, 'loadfile');
t_d = 6;
Tts = t_d * 24 * 60 * 60 / 300;
% 
% % === TOC Seasonality Pattern ===
load Stream_demands_competition_6days.mat % Demands that were created in Step 1
steps_per_day = 288;
days_in_month = [31,28,31,30,31,30,31,31,30,31,30,31];
seasonality_factors_TOC = [0.95,0.90,0.85,0.80,0.85,0.90,1.00,1.10,1.15,1.20, 1.10,1];

% Create daily-seasonality multiplier vector
C_SRA_REPAT_vec = zeros(Tts, 1);
TOC_multiplier = seasonality_factors_TOC(month_idx);
C_SRA_REPAT_vec = repmat(TOC_multiplier, Tts, 1);

d.setTimeSimulationDuration(t_d * 24 * 60 * 60);

% Define msx file
msx={};
msx.FILENAME = './Challenge/AI_challenge6days.msx';

% Section Title
msx.TITLE = {'AI Challenge'};

% Section Options
msx.AREA_UNITS = 'FT2'; %AREA_UNITS FT2/M2/CM2
msx.RATE_UNITS = 'HR'; %TIME_UNITS SEC/MIN/HR/DAY
msx.SOLVER = 'RK5'; %SOLVER EUL/RK5/ROS2
msx.TIMESTEP = 300; %TIMESTEP in seconds
msx.RTOL = 0.001;  %RTOL value
msx.ATOL = 0.001;  %ATOL value

% Section Species
% <type> <specieID> <units> (<atol> <rtol>)
msx.SPECIES(1) = {'BULK CL2 MG 0.01 0.001'}; % Chlorine
msx.SPECIES(2) = {'BULK P CFU 0.01 0.001'}; % Pathogen
msx.SPECIES(3) = {'BULK C_FRA MG 0.01 0.001'}; %Fast reducing agent
msx.SPECIES(4) = {'BULK C_SRA MG 0.01 0.001'}; % Slow reducing agent

% Section Coefficients
% CONSTANT name value % PARAMETER name value
msx.COEFFICIENTS(1) = {'CONSTANT T 12'}; % Water temperature in degree C
msx.COEFFICIENTS(2) = {'CONSTANT Kp 92.3'}; % Inactivation rate
msx.COEFFICIENTS(3) = {'CONSTANT A 1'}; % Aplification factor (dm/h), decimeter Monteiro et al 2020
msx.COEFFICIENTS(4) = {'CONSTANT B 14 '}; % Rate coefficient (L/MG)

% Section Terms
% <termID> <expression>
msx.TERMS(1) = {'Km (1.5826e-04 * RE^0.88 )/ D'}; %Mass transport coeff (dm/h), taken from epanet-msx manual(ft/h)
msx.TERMS(2) = {'KWAL A*EXP(-B*CL2)'};
msx.TERMS(3) = {'K_FAST 0.2808'}; % Monteiro
msx.TERMS(4) = {'K_SLOW 0.0071'}; % Monteiro

% Section Pipes
% EQUIL <specieID> <expression> % RATE <specieID> <expression> % FORMULA <specieID> <expression>
msx.PIPES(1) = {'RATE CL2 -K_FAST*C_FRA*CL2-K_SLOW*C_SRA*CL2-((4/D)*(KWAL/(1+KWAL/Km)))*CL2'};
msx.PIPES(2) = {'RATE P -Kp*P*CL2'};
msx.PIPES(3) = {'RATE C_FRA -K_FAST*C_FRA*CL2'};
msx.PIPES(4) = {'RATE C_SRA -K_SLOW*C_SRA*CL2'};

% Section Tanks
% EQUIL <specieID> <expression> % RATE <specieID> <expression> % FORMULA <specieID> <expression>
msx.TANKS(1) = {'RATE CL2 -K_FAST*C_FRA*CL2-K_SLOW*C_SRA*CL2'};
msx.TANKS(2) = {'RATE P -Kp*P*CL2'};
msx.TANKS(3) = {'RATE C_FRA -K_FAST*C_FRA*CL2'};
msx.TANKS(4) = {'RATE C_SRA -K_SLOW*C_SRA*CL2'};

% Section Sources
% Set boundaries and variability for TOC entering the network through the
% reservoir
CL2_RES_min=0.4; %mg/l
CL2_RES_max=0.6; %mg/l
CL2_RES = CL2_RES_min + (CL2_RES_max-CL2_RES_min)* rand;
TOC_RES_min=1; % mg/l
TOC_RES_max=5; % mg/l
TOC_RES = TOC_RES_min + (TOC_RES_max-TOC_RES_min)* rand;

% <type> <nodeID> <specieID> <strength> (<patternID>)
msx.SOURCES(1) = {['SETPOINT WTP CL2 ', num2str(CL2_RES), ' CL2PAT']};
msx.SOURCES(2) = {['SETPOINT WTP C_SRA ', num2str(TOC_RES), ' C_SRA_REPAT']}; 

% Booster chlorination
cl2_nodes = {'dist423', 'dist225', 'dist989','dist1283','dist1931'};
cl2_doses = [0.2,0.2, 0.2, 0.2, 0.2];
cl2_patterns = {'CL2PAT1', 'CL2PAT2', 'CL2PAT3', 'CL2PAT4', 'CL2PAT5'};
for i = 1:numel(cl2_nodes)
    msx.SOURCES{end+1} = ['MASS ', cl2_nodes{i}, ' CL2 ', num2str(cl2_doses(i)), ' ', cl2_patterns{i}];
end


% % === Generate 1 contamination event (random time on Day 5) ===
steps_per_day = 288;
Tts = 6 * steps_per_day;

event_start = (5 - 1) * steps_per_day + randi([1, steps_per_day]);  % Day 5
event_duration = randi([12, 96]);
event_end = min(event_start + event_duration, Tts);

all_nodes = d.getNodeNameID;
all_nodes([255, 256]) = [];
dist_nodes = all_nodes(startsWith(all_nodes, 'dist'));

% Filter out dead-end nodes (only keep well-connected ones)
link_ends = d.getLinkNodesIndex;
num_nodes = d.getNodeCount;
node_conn_count = zeros(1, num_nodes);
for i = 1:size(link_ends, 1)
    node_conn_count(link_ends(i,1)) = node_conn_count(link_ends(i,1)) + 1;
    node_conn_count(link_ends(i,2)) = node_conn_count(link_ends(i,2)) + 1;
end
dist_indices = find(startsWith(all_nodes, 'dist'));
safe_indices = dist_indices(node_conn_count(dist_indices) > 1);
dist_nodes_filtered = all_nodes(safe_indices);
source_node = dist_nodes_filtered{randi(numel(dist_nodes_filtered))};

% Concentrations
EV_log_min = log10(1.39e6);
EV_log_max = log10(2.08e7);
EV_conc = 10^(EV_log_min + rand * (EV_log_max - EV_log_min));
TOC = 140 + rand * (250 - 140);
C_FRA_fraction = 0.4;
C_SRA_fraction = 0.6;
rate = 100;
injection_conc_P = EV_conc * rate;
injection_conc_C_FRA = C_FRA_fraction * TOC * rate;
injection_conc_C_SRA = C_SRA_fraction * TOC * rate;

% Generate patterns
PathPAT = zeros(1, Tts);
C_FRAPAT = zeros(1, Tts);
C_SRAPAT = zeros(1, Tts);
PathPAT(event_start:event_end) = injection_conc_P;
C_FRAPAT(event_start:event_end) = injection_conc_C_FRA;
C_SRAPAT(event_start:event_end) = injection_conc_C_SRA;

% === Add sources and patterns ===
msx.SOURCES{end+1} = ['MASS ', source_node, ' P 1 PathPAT'];
msx.SOURCES{end+1} = ['MASS ', source_node, ' C_FRA 1 C_FRAPAT'];
msx.SOURCES{end+1} = ['MASS ', source_node, ' C_SRA 1 C_SRAPAT'];


%%Section Parameters
%PIPE <pipeID> <paramID> <value> % TANK <tankID> <paramID> <value>
%Calculation of wall chlorine decay parameters.
nl=double(d.getLinkCount);
B=14;
for m =1:nl
    indp = d.getLinkNameID{m};
    if d.getLinkRoughnessCoeff(m)>=140
        A=0.01;
    else
        A=rand(1);
    end
    msx.PARAMETERS(m) = {['PIPE ',indp,' A ',num2str(A)]};
    msx.PARAMETERS(nl+m) = {['PIPE ',indp,' B ',num2str(B)]};
end


% === Add static patterns ===
msx.PATTERNS{1} = {'CL2PAT 1'};
msx.PATTERNS{2} = {'C_SRA_REPAT 1'};
msx.PATTERNS{3} = {'PathPAT 1'};
msx.PATTERNS{4} = {'C_FRAPAT 1'};
msx.PATTERNS{5} = {'C_SRAPAT 1'};
msx.PATTERNS{6} = {'CL2PAT1 1'};
msx.PATTERNS{7} = {'CL2PAT2 1'};
msx.PATTERNS{8} = {'CL2PAT3 1'};
msx.PATTERNS{9} = {'CL2PAT4 1'};
msx.PATTERNS{10} = {'CL2PAT5 1'};

% Write MSX
d.writeMSXFile(msx);
d.loadMSXFile(msx.FILENAME);

% === Add dynamic patterns ===
d.setMSXPattern('PathPAT',   PathPAT);
d.setMSXPattern('C_FRAPAT',  C_FRAPAT);
d.setMSXPattern('C_SRAPAT',  C_SRAPAT);
d.setMSXPattern('C_SRA_REPAT',  C_SRA_REPAT_vec);
d.saveMSXFile(msx.FILENAME)
% Printing
fprintf('MSX File written successfully.\n');

% % % Save all event metadata for tracking and future evaluation
 save('contamination_metadata_6days.mat', ...
    'event_start', 'event_duration','event_end', 'source_node', ...
    'injection_conc_P', 'injection_conc_C_FRA', 'injection_conc_C_SRA', ...
    'PathPAT', 'C_FRAPAT', 'C_SRAPAT', ...
    'CL2_RES', 'TOC_RES', 'C_SRA_REPAT_vec','dist_nodes', 'dist_indices');