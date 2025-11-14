% 1. Setup Scenario
%%%%%%%% Step 1: Create new Demands %%%%%%%%%
try
d.unload
catch ERR
end 
fclose all;clear class;clear all;clc;close all;
% Start EPANET MATLAB TOOLKIT
addpath(genpath(pwd));
disp('EPANET-MATLAB Toolkit Paths Loaded.'); 
inpname = 'CY-DBP_competition_final.inp';
d = epanet(inpname);
t_d = 6;
duration_sec = t_d * 24 * 60 * 60;
d.setTimeSimulationDuration(duration_sec);
d.setTimeReportingStep(300)
d.setTimeHydraulicStep(300)
d.setTimePatternStep(300)

hydraulics = d.getComputedTimeSeries;

%%% Calculate initial hydraulics
Demand= hydraulics.Demand(:,d.getNodeJunctionIndex);
Demand= Demand.*1000;  %CMH to L/h
Demand(:, [255, 256]) = [];  % Removes columns 255 and 256

K= 288;
Dt= double(d.getTimeHydraulicStep)/3600;
Vpd= 150;
V_sc=cumsum(Demand(1:K,:),1)*Dt; %Calculate volume consumed per node in 24 hours
People_per_node= V_sc(end,:)/Vpd; % People per node 
% 
Node = d.getNodeNameID;
junctionIndex = d.getNodeJunctionIndex;
Node = Node(junctionIndex);  
Node([255, 256]) = [];
%% ::: STREAM :::
% % AVAILABLE FIXTURES
% % 1. toilet
% % 2. shower
% % 3. faucet
% % 4. clothes washer
% % 5. dishwasher
% % 6. bathtub
%% ::: INPUT SETTINGS :::
%% ::: LOADING COMPLETE DATABASE :::
load database.mat

People_per_node_rnd= round(People_per_node);
Population_unc=0.1;
for i=1:length(People_per_node_rnd)
    disp(['Simulating Node ',num2str(i),' of ',num2str(length(People_per_node_rnd))])
    % Create +-10% uncertainty
    Population=People_per_node_rnd(i);
    Population_l=Population-Population_unc*Population;
    Population_u=Population+Population_unc*Population;
    Population=Population_l+rand(1,length(Population)).*(Population_u-Population_l);
    Population = round(Population);

%input population
home=0;
%initialization
StToilet=0;
StShower=0;
StFaucet=0;
StClothesWasher=0;
StDishwasher=0;
TOTAL=0;

while Population>0

% --- A. Household size setting
home=home+1;
param.HHsize = randi(5,1); % This parameter should be in the interval (1,6).
% From 1 to 5, it indicates the number of people living in the house. 6 means ">5".

Population=Population-param.HHsize;
% --- B. Water consuming fixtures selection
% Legend:
% 0 = not present
% 1 = present

param.appliances.StToilet = 1;
param.appliances.HEToilet = 0;

param.appliances.StShower = 1;
param.appliances.HEShower = 0;

param.appliances.StFaucet = 1;
param.appliances.HEFaucet = 0;

param.appliances.StClothesWasher = 1;
param.appliances.HEClothesWasher = 0;

param.appliances.StDishwasher = 1;
param.appliances.HEDishwasher = 0;

param.appliances.StBathtub = 1;
param.appliances.HEBathtub = 0;

% --- C. Time horizon length setting
param.H = 365; % It is measured in [days]

% --- D. Time sampling resolution
param.ts = 30; % It is measured in [10 seconds] units. The maximum resolution allowed is 10 seconds (param.ts = 1).

% Setting the seed
% rng(1);

% Parameters structure settings and check
% Checking input consistency
temp=checkInput(param);
% clearvars -except param

%%% ::: WATER END-USE TIME SERIES GENERATION :::

% Initialization
outputTrajectory = initializeTrajectories(param);
% Include the first step
appNames = fieldnames(outputTrajectory);
for app=appNames'
    outputTrajectory.(char(app))=zeros(1,length(outputTrajectory.TOTAL)+30);
end

% End-use water use time series generation
outputTrajectory = generateConsumptionEvents(outputTrajectory, param, database);
% disp('End-use consumption trajectories created');

% Total water use time series aggregation
outputTrajectory = sumToTotal(outputTrajectory);
% disp('Total consumption trajectory created');

% Data scaling to desired sampling resolution
outputTrajectory = aggregateSamplingResolution(outputTrajectory, param);
% disp('Data scaled to desired sampling resolution');

StToilet=outputTrajectory.StToilet+StToilet;
StShower=outputTrajectory.StShower+StShower;
StFaucet=outputTrajectory.StFaucet+StFaucet;
StClothesWasher=outputTrajectory.StClothesWasher+StClothesWasher;
StDishwasher=outputTrajectory.StDishwasher+StDishwasher;
TOTAL=outputTrajectory.TOTAL+TOTAL;
clear outputTrajectory;
end

output.output.(Node{i}).StToilet=StToilet;
output.output.(Node{i}).StShower=StShower;
output.output.(Node{i}).StFaucet=StFaucet;
output.output.(Node{i}).StClothesWasher=StClothesWasher;
output.output.(Node{i}).StDishwasher=StDishwasher;
output.output.(Node{i}).TOTAL=TOTAL;
end

% --- Cleanup: remove final timestep from each trajectory if oversized
fields_to_trim = {'StToilet', 'StShower', 'StFaucet', 'StClothesWasher', 'StDishwasher', 'TOTAL'};
expected_length = 365 * 288;  % = 105120
output2=output;

for i = 1:length(People_per_node_rnd)
    node_id = Node{i};
    for f = 1:length(fields_to_trim)
        fieldname = fields_to_trim{f};
        series = output.output.(node_id).(fieldname);
        if length(series) > expected_length
            output2.output.(node_id).(fieldname) = series(1:expected_length);
        end
    end
end

Stream_demand_tot=[];
Stream_demand_Faucet=[];
expected_length = (365*288);
for j = 1:length(People_per_node_rnd)
    node_id = Node{j};

    if isfield(output.output, node_id)
        total_series = output2.output.(node_id).TOTAL;
        faucet_series = output2.output.(node_id).StFaucet;

        % Expand scalar zero to full-length zero vector
        if isscalar(total_series)
            total_series = zeros(expected_length, 1);
        end
        if isscalar(faucet_series)
            faucet_series = zeros(expected_length, 1);
        end

        % Enforce column vector format
        total_series = total_series(:);
        faucet_series = faucet_series(:);

        Stream_demand_tot(:, end+1) = total_series;
        Stream_demand_Faucet(:, end+1) = faucet_series;
    else
        % Fill with zeros if somehow the node field is missing
        Stream_demand_tot(:, end+1) = zeros(expected_length, 1);
        Stream_demand_Faucet(:, end+1) = zeros(expected_length, 1);
    end
end

% Convert from L/5min to CMH
Stream = (Stream_demand_tot .* 12) / 1000;
Stream_faucet = (Stream_demand_Faucet .* 12) / 1000; 

% Apply random multiplier  between 0.8 and 1.2
steps_per_day = 288;
days_in_month = [31,28,31,30,31,30,31,31,30,31,30,31];
seasonality_factors = [0.85, 0.9, 1.0, 1.05, 1.10, 1.15, 1.2, 1.2, 1.1, 1.0, 0.9, 0.85];

multiplier_vector = [];
for i = 1:12
    reps = days_in_month(i) * steps_per_day;
    multiplier_vector = [multiplier_vector; repmat(seasonality_factors(i), reps, 1)];
end

% Truncate to match simulation length (365 * 288)
multiplier_vector = multiplier_vector(1:(365 * steps_per_day));

Stream = Stream .* multiplier_vector;
Stream_faucet = Stream_faucet .* multiplier_vector;


% Saving
save ('./Stream_demands_competition_365days.mat','output','output2','Stream','Stream_faucet','People_per_node', 'multiplier_vector')

%--------------------------------------------------------------------------%