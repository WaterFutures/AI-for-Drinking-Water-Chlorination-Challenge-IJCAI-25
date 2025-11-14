%%%%%%%%% Step 2: Assign new Demands %%%%%%%%%
try 
d.unload
catch ERR
end 
fclose all;clear class;
close all;clear all;clc;
addpath(genpath(pwd));
% % Start EPANET MATLAB TOOLKIT
%% Load Network:
inpname = 'CY-DBP_competition_final.inp';
dispname = 'CY-DBP_competition';
d=epanet(inpname);
nj=d.getNodeJunctionCount;
nn=d.getNodeCount;

% % Assign demands to network:
% Get existing patterns:
%     d.getNodeDemandPatternIndex{categoryIndex}(nodeIndex)
demInd1 = double(d.getNodeDemandPatternIndex{1}(:)); 
demInd1G = demInd1;
baseDemInd1 = double(d.getNodeBaseDemands{1}(:));

% Zero base demands
for i=1:nj-2
    disp(['Zero base demand ',num2str(i)])
    d.setNodeBaseDemands(i, 1, 0)
end

% Delete old pattern:
patternIndex = 2:3;
patterns_values=d.getPattern;
pattern_ids= d.getPatternNameID;
pattern_ids=pattern_ids(patternIndex);
d.deletePatternAll;
for ll=1:length(pattern_ids)
    d.addPattern(pattern_ids{ll},patterns_values(patternIndex(ll),:))
end


% Save new input file:
emptyInpName = ['networks\',dispname,'_empty_3days','.inp'];
d.saveInputFile(emptyInpName);
disp('EMPTY NETWORK READY!')

% Load new actual demands:
load Stream_demands_competition_6days.mat % Demands that were created in Step 1

% Calculate and assign new base demands:

d=epanet(emptyInpName);
% === Set correct simulation time for 3 days ===
d.setTimeHydraulicStep(300);     % 5-min timestep
d.setTimePatternStep(300);
d.setTimeReportingStep(300);
t_d = 6;
duration_sec = t_d * 24 * 60 * 60;
d.setTimeSimulationDuration(duration_sec);

demInd1 = demInd1G;

base_Stream_demand = mean(Stream);
for i=1:size(Stream,2)
    disp(['Assign base demand ',num2str(i)])
    d.setNodeBaseDemands(i, 1, base_Stream_demand(i))
end

% Calculate new patterns:
pattern_Stream_demand = Stream./base_Stream_demand;
pattern_Stream_demand(isnan(pattern_Stream_demand))=0;

% Add new patterns:
for i = 1:size(Stream,2)
    demands = pattern_Stream_demand(:,i);
    resDemPatInd(i)=d.addPattern(['P-Res-',num2str(i)],demands);
    disp(['Creating pattern Residential ',num2str(i)])
    disp(['Indexing pattern ',num2str(i),' category 1'])
    if demInd1(i)==0
        continue 
    elseif demInd1(i)==1 % Residential
        demInd1(i)=resDemPatInd(i);
    else
        error('unknown demand pattern')
    end
end

% Assign new patterns:
for i=1:nj-2
    disp(['Assigning pattern ',num2str(i),' out of ',num2str(nj-2)])
    d.setNodeDemandPatternIndex(i, 1, demInd1(i))
end

d.setNodeDemandPatternIndex(255, 1, 2);
d.setNodeDemandPatternIndex(256, 1, 1);

% Correct times:
d.setTimeReportingStep(300)
d.setTimeHydraulicStep(300)
d.setTimePatternStep(300)

% Save new input file:
newInpname = ['networks\',dispname,'_stream_competition_6days.inp'];
d.saveInputFile(newInpname);
disp('NETWORK READY!')

%--------------------------------------------------------------------------%