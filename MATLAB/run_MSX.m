%% 2. Run scenario
try 
d.unload
catch ERR
end 
fclose all;clear class;clear all;clc;close all;
addpath(genpath(pwd));
t_d = 6;
inpname = 'networks\CY-DBP_competition_stream_competition_6days.inp';
d = epanet(inpname);
d.setTimeSimulationDuration(t_d * 24 * 60 * 60);  % 365 days × 24h × 3600s
Tts = t_d * 24 * 60 * 60 / 300;
% % % % %%=== Load MSX ===
msx_filename = './Challenge/AI_challenge6days.msx';
d.loadMSXFile(msx_filename);  % Load compiled MSX file
load('contamination_metadata_6days.mat'); % needed for event_map and patterns

% === Solve hydraulics once ===
d.solveMSXCompleteHydraulics;
% === Initialize MSX ===
d.initializeMSXQualityAnalysis(0);

% === Preallocate storage ===
nn = d.getNodeCount;
ns = d.MSXSpeciesCount;
species_names = d.getMSXSpeciesNameID;
value.Quality = cell(nn, 1);
value.Time = [];

% === Initial quality values ===
for i = 1:nn
    for j = 1:ns
        [~, value.Quality{i}(1, j)] = d.apiMSXgetinitqual(0, i, j, d.MSXLibEPANET);
        % [~, value.Quality{i}(1, j)] = d.getMSXNodeInitqualValue(i, j);
    end
end

% === Step-by-step simulation ===
k = 1;
tleft = 1;
value.Time(k, :) = 0;
previous_day = 0;
while tleft > 0
    [~, t, tleft] = d.apiMSXstep(d.MSXLibEPANET);
    % [~, t, tleft] = d.stepMSXQualityAnalysisTimeLeft;
    current_day = floor(t / 86400) + 1;

    if current_day ~= previous_day
        fprintf('Simulating Day %d of %d\n', current_day, t_d);
        previous_day = current_day;
    end
    for i = 1:nn
        for j = 1:ns
            [~, value.Quality{i}(k+1, j)] = d.apiMSXgetqual(0, i, j, d.MSXLibEPANET);
            % [~, value.Quality{i}(1, j)] = d.getMSXNodeInitqualValue(i, j);
        end
    end
    value.Time(k+1, :) = t;
    k = k + 1;
end

save('./AI_Challenge_step_by_step_MSX_API_6days_final.mat', 'value', 'species_names');

disp('Simulation finished.');
% --------------------------------------------------------------------------%
% --------------------------------------------------------------------------%
% --------------------------------------------------------------------------%