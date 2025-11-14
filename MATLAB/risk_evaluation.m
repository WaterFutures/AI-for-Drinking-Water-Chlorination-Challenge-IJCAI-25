%%%%%%%% Step 3: Setup MSX file %%%%%%%%%
% %% Infection Risk Evaluation
try 
d.unload
catch ERR
end 
fclose all;clear class;clear all;clc;close all;
addpath(genpath(pwd));
inpname = 'networks\CY-DBP_competition_stream_competition_6days.inp';
d = epanet(inpname);
% % % Load input data
load('Stream_demands_competition_6days.mat');
load('AI_Challenge_step_by_step_MSX_API_6days_final.mat'); % contains 'value', 'species_names'
load('contamination_metadata_6days.mat'); % contains durations, source_nodes, concentrations
% % % % % Constants
r_entero = 0.014472;  % dose-response parameter for Enterovirus
steps_per_day = 288;

% Preprocess input
People_per_node = round(People_per_node);
Stream = Stream * 1000;
Stream_faucet = Stream_faucet * 1000;
numJunctions = length(dist_nodes);
Dt = double(d.getTimeHydraulicStep) / 3600;

% Extract pathogen concentrations
num_nodes = length(dist_nodes);
num_timesteps = size(value.Quality{1}, 1);
Pathogen_concentration = zeros(num_timesteps, num_nodes);
for i = 1:num_nodes
    Pathogen_concentration(:, i) = value.Quality{i}(:, strcmp(species_names, 'P'));
end

% Loop through each contamination event
% Infection Risk Evaluation for single event
disp('Processing single contamination event...');
% Align to full day containing the event start
aligned_start = max(1, event_start - 1);  % Start one timestep before contamination
aligned_end   = min(aligned_start + steps_per_day - 1, size(Stream_faucet, 1)); % 288 steps total

% Extract aligned data
Stream_tap = round(Stream_faucet(aligned_start:aligned_end, :));
cont_matrix = Pathogen_concentration(aligned_start:aligned_end, dist_indices);

% Consumption matrix setup
stream_tot = sum(Stream_tap, 1);
fraction = People_per_node ./ stream_tot;
fraction(isinf(fraction)) = 0;
Consumed_Stream = Stream_tap .* fraction;

% Distribute per person (max 1L/day, 0.25L/step)
Volume = cell(1, numJunctions);
for m = 1:numJunctions
    Volume{m} = zeros(size(Stream_tap, 1), People_per_node(m));
    for n = 1:People_per_node(m)
        for t = 1:size(Stream_tap, 1)
            while Consumed_Stream(t, m) > 0
                if Consumed_Stream(t, m) < 0.00001
                    break;
                end
                if sum(Volume{m}(:, n)) < 1
                    delta = min([0.25, 1 - sum(Volume{m}(:, n)), Consumed_Stream(t, m)]);
                    Volume{m}(t, n) = Volume{m}(t, n) + delta;
                    Consumed_Stream(t, m) = Consumed_Stream(t, m) - delta;
                end
                n = mod(n, People_per_node(m)) + 1;
            end
        end
    end
end

% Dose & risk calculations
Dose = cell(1, numJunctions);
Risk = cell(1, numJunctions);
Total_risk_per_person = cell(1, numJunctions);
Total_infections_ts = zeros(numJunctions, steps_per_day);

for m = 1:numJunctions
    Dose{m} = Volume{m} .* cont_matrix(:, m);
    Risk{m} = 1 - exp(-r_entero * Dose{m});

    for p = 1:People_per_node(m)
        Total_risk_per_person{m}(p) = 1 - prod(1 - Risk{m}(:, p));
    end
    if isempty(Risk{m})
        continue;  % Skip if dead-end node or no consumers
    end

    cum_risk = zeros(size(Risk{m}));
    cum_risk(:, 1) = Risk{m}(:, 1);
    for t = 2:steps_per_day
        for p = 1:People_per_node(m)
            cum_risk(t, p) = 1 - (1 - cum_risk(t - 1, p)) * (1 - Risk{m}(t, p));
        end
    end
    Total_infections_ts(m, :) = sum(cum_risk, 2)';
end

% Store results
Total_Infections_day = sum(cell2mat(Total_risk_per_person));
Total_risk_of_infection = (Total_Infections_day / sum(People_per_node)) * 100;
Total_infections_per_timestep_aggregated = sum(Total_infections_ts, 1);

Event_Results.Dose = Dose;
Event_Results.Risk = Risk;
Event_Results.Total_risk_per_person = Total_risk_per_person;
Event_Results.Total_infections_day = Total_Infections_day;
Event_Results.Total_risk_pct = Total_risk_of_infection;
Event_Results.Infections_ts = Total_infections_per_timestep_aggregated;

%% Save results
save('AI_Challenge_infection_risk_results_6days_final.mat', ...
    'Event_Results', 'People_per_node', ...
    'source_node');

disp('Infection risk evaluation complete.');