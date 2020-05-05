%
%      .o.       ooooooooo.         .o.       oooooo     oooo 
%     .888.      `888   `Y88.      .888.       `888.     .8'  
%    .8"888.      888   .d88'     .8"888.       `888.   .8'   
%   .8' `888.     888ooo88P'     .8' `888.       `888. .8'    
%  .88ooo8888.    888`88b.      .88ooo8888.       `888.8'     
% .8'     `888.   888  `88b.   .8'     `888.       `888'      
%o88o     o8888o o888o  o888o o88o     o8888o       `8'       
%                                                             
% GetARAVdata
%% Script summary
%
% Author: Ant8ony Aboumrad
% Date: 17 April 2020
% Project: Autonomous Recharging of Aerial Vehicles (ARAV)
%
% 'GetARAVdata' is a script that processes and visualizes data from an
% Excel spreadsheet export of "Summary of Tests Conducted", a shared Google
% Sheets document. The target spreadheet contains test data for Autonomous
% Recharging of Aerial Vehicles (ARAV), a Sonoma State University
% Engineering Department Senior Design Project (Spring 2020).
%
% NOTE: This script assumed that the target file is located in the current
% working directory, and has table-formatted data on the worksheets named
% below. A modification of worksheet names and/or data formatting may
% produce runtime errors.
%
% The last portion of this script saves all generated figures as PNG files,
% and requires a local subdirectory named "ARAV_figures/"
%

%% Retreive table data from worksheets

filename = 'Summary of Tests Conducted.xlsx';

% Worksheet name definitions, uncomment as used, MUST VERIFY REGULARLY
commandSheet = 'FT.1.1.1';
swLandAccSheet = 'FT.2.2.1';
% chargeTimeSheet = 'FT.3.4.1';
camPowerSheet = 'FT.4.5.1';
% qiPowerSheet = 'FT.4.5.2';
sbcPowerSheet = 'FT.4.5.3';
% systemBattSheet = 'ST.4.5.1';
% hoverEnduranceSheet = 'FT.5.6.1';
% mobilityEnduranceSheet = 'FT.5.6.2';
landingDurationSheet = 'FT.5.6.3';
detectionRangeSheet = 'FT.6.7.1';
% dimensionSheet = 'ST.8.8.1';
% networkAccessSheet = 'FT.9.9.1';
% anchorPointSheet = 'ST.10.10.1';
% etc...

sheetnames = {commandSheet, swLandAccSheet, landingDurationSheet, detectionRangeSheet, camPowerSheet, sbcPowerSheet;...
    'commandResponse', 'swLandAcc', 'landingTime', 'detectionRange', 'camPower', 'sbcPower'};

% for each defined sheet, read one at a time and then close
[~,numsheets]=size(sheetnames);
for f=1:numsheets
    T = readtable(filename,'ReadRowNames',true,'Sheet',sheetnames{1,f});
    %     eval([sheetnames{2,f} '_header = headertext;']);
    eval([sheetnames{2,f} '_table = T;']);
end
clear f T numsheets

%% Analyze Command Response test results
%ignore first row of initial timestamp
commandResponse_array = table2array(commandResponse_table(2:end,:));
% get just the latency data series to plot
commandResponse_y = commandResponse_array(:,[2 5 8 11 14 17 20 23]);
% convert seconds to milliseconds
commandResponse_y = commandResponse_y*1000;
% distance (m) for x
commandResponse_x = commandResponse_array(1,[3 6 9 12 15 18 21 24]);

% get stats (mean +/- 95% CI)
[~,numcol]=size(commandResponse_y);
commandResponseStats = zeros(7,numcol);
for i=1:numcol
    % default CI = 95% (alpha=0.05)
    [mean,sigma,meanCI,sigmaCI] = normfit(commandResponse_y(~isnan(commandResponse_y(:,i)),i));
    commandResponseStats(1:6,i) = [mean sigma meanCI' sigmaCI']';
    % include sample size in stats array
    [commandResponseStats(7,i),~] = size(commandResponse_y(~isnan(commandResponse_y(:,i)),i));
end
clear numcol i mean sigma meanCI sigmaCI

% get error val from series stats
cl_errs = commandResponseStats(1,:)-commandResponseStats(3,:);

% plot Command Latency avgs w/ error bars
latencyFig = figure;
cl_plot = errorbar(commandResponse_x,commandResponseStats(1,:),cl_errs);
clAx = gca;
% bar plot formatting
cl_plot.LineStyle='none';
cl_plot.Marker='*';
cl_plot.MarkerSize=7;
cl_plot.MarkerEdgeColor='red';
cl_plot.MarkerFaceColor='red';
% figure formatting
xlabel(clAx,'Distance (m)')
ylabel(clAx,'Latency (ms)')
title(clAx,{'UAV Command Latency vs Distance','(n \geq 450 for each trial)'})
ylim(clAx,[9.5,10.5])
xlim(clAx,[-0.2,3.5])

% No command failures = satisfies MR-1 & ER-1, 100% success w/ sample size
commandReliableSampleSize = sum(~isnan(commandResponse_y),'all')

%% Analyze Software Landing Accuracy test results

% get all landing accuracy series, excluding NaN
swLand_array = table2array(swLandAcc_table);
[~,numcol]=size(swLand_array);
for i=1:numcol
    eval(['swLand_y' num2str(i) ' = swLand_array(~isnan(swLand_array(:,' num2str(i) ')),' num2str(i) ');'])
end
clear numcol i

% get stats for Frame diff vs. IR accuracy mean and CI
swLandStats = zeros(7,2);

% default CI = 95% (alpha=0.05)
[mean,sigma,meanCI,sigmaCI] = normfit(swLand_y2);
swLandStats(1:6,1) = [mean sigma meanCI' sigmaCI']';
[mean,sigma,meanCI,sigmaCI] = normfit(swLand_y3);
swLandStats(1:6,2) = [mean sigma meanCI' sigmaCI']';
% include sample size in stats array
[swLandStats(7,1),~] = size(swLand_y2);
[swLandStats(7,2),~] = size(swLand_y3);

clear mean sigma meanCI sigmaCI


% Plot no-feedback landing accuracy to histogram
swLandFig_1 = figure;
hold on
h1_plot = histogram(swLand_y1);
h1_plot.FaceColor = [0, 0.4470, 0.7410];
h1_plot.Normalization = 'probability';
h1_plot.BinWidth = 5;
h1Ax = gca;
ylim(h1Ax,[0,0.35])
title(h1Ax,{'Probability Density of Software Landing Accuracy,',['No Image Tracking (n = ' num2str(numel(swLand_y1)) ')']})
%ylabel(h1Ax,'Probability');
xlabel(h1Ax,'Landing Accuracy (cm)');

% Plot accuracy w/ image feedback to histograms (subplot for Frame Diff and IR test results)
swLandFig_2 = figure;
hold on
%   Frame diff
subplot(2,1,1)
h2_plot = histogram(swLand_y2);
h2_plot.FaceColor = [0.8500, 0.3250, 0.0980];
h2_plot.Normalization = 'probability';
h2Ax = gca;
[numrows,~] = size(swLand_y2);
title(h2Ax,['Frame Difference Tracking (n = ' num2str(numrows) ')'])
ylim(h2Ax,[0,0.3])
%   IR beacon
subplot(2,1,2)
h3_plot = histogram(swLand_y3);
h3_plot.FaceColor = [0, 0.4470, 0.7410];
h3_plot.Normalization = 'probability';
h3Ax = gca;
[numrows,~] = size(swLand_y3);
title(h3Ax,['Infrared LED Tracking (n = ' num2str(numrows) ')'])
ylim(h3Ax,[0,0.3])
%   shared figure labels
hax=axes(swLandFig_2,'visible','off');
hax.Title.Visible='on';
hax.XLabel.Visible='on';
hax.YLabel.Visible='on';
%ylabel(hax,'Probability');
xlabel(hax,'Landing Accuracy (cm)');
% title(hax,'Software Landing Accuracy with Image Recognition');
sgtitle('Probability Density of Software Landing Accuracy')

clear numrows

%% Analyze Landing Sequence Duration test results
%ignore first row of initial timestamp
landingTime_array = table2array(landingTime_table);
% get just the time data series (Frame Diff and IR)
landingTime_y = landingTime_array(:,[1 3]);
% get stats (mean +/- 95% CI)
[~,numcol]=size(landingTime_y);
landingTimeStats = zeros(7,numcol);
for i=1:numcol
    % default CI = 95% (alpha=0.05)
    eval(['landingTime_y' num2str(i) ' = landingTime_y(~isnan(landingTime_y(:,' num2str(i) ')),' num2str(i) ');'])
    [mean,sigma,meanCI,sigmaCI] = normfit(landingTime_y(~isnan(landingTime_y(:,i)),i));
    landingTimeStats(1:6,i) = [mean sigma meanCI' sigmaCI']';
    % include sample size in stats array
    eval(['[landingTimeStats(7,i),~] = size(landingTime_y' num2str(i) ');'])
    
end
clear numcol i mean sigma meanCI sigmaCI landingTime_y
lt_errs = landingTimeStats(1,:)-landingTimeStats(3,:);

% plot bars for Landing times
landingTimeFig = figure;
lt_plot = bar(landingTimeStats(1,:),'FaceColor',[0, 0.4470, 0.7410]);
% lt_plot.FaceColor = [0, 0.4470, 0.7410];
ltAx = gca;
% figure formatting
xticks(ltAx,[1 2])
xticklabels(ltAx,{['Frame Difference Tracking (n = ' num2str(landingTimeStats(7,1)) ')'],...
    ['Infrared LED Tracking (n = ' num2str(landingTimeStats(7,2)) ')']})
xlim(ltAx,[0.5 2.5])
ylabel(ltAx,'duration (s)')
title(ltAx,'Landing Sequence Duration vs Image Tracking Method')
ylim(ltAx,[30,170])
for i = 1:numel(xticks)
    text(i,landingTimeStats(1,i)+ 5,[num2str(round(landingTimeStats(1,i),3))...
        '\pm' num2str(round(lt_errs(i),3))], 'HorizontalAlignment', 'center')
end
clear i

% Box plots for landing times..
swLandFig_3 = figure;
hold on
%   Frame diff
subplot(2,1,1)
b2_plot = boxplot(landingTime_y1, 'Orientation','horizontal');
b2Ax = gca;
% find corners of box and color fill using 'patch'
b2 = findobj(b2Ax,'Tag','Box');
patch(b2Ax, get(b2,'XData'),get(b2,'YData'),[0.8500, 0.3250, 0.0980],'FaceAlpha',.5);
% force median line to black for contrast
set(b2Ax.Children(2).Children(2),'Color','k')
% remove dummy YTick label
set(b2Ax,'YTickLabel',{' '})
[numrows,~] = size(landingTime_y1);
title(b2Ax,{' ',['Frame Difference Tracking (n = ' num2str(numrows) ')']})
% ylim(b2Ax,[0,0.3])

%   IR beacon
subplot(2,1,2)
b3_plot = boxplot(landingTime_y2, 'Orientation','horizontal');
b3Ax = gca;
b3 = findobj(b3Ax,'Tag','Box');
patch(b3Ax, get(b3,'XData'),get(b3,'YData'),[0, 0.4470, 0.7410],'FaceAlpha',.5);
% force median line to black for contrast
set(b2Ax.Children(2).Children(2),'Color','k')
% remove dummy YTick label
set(b3Ax,'YTickLabel',{' '})
[numrows,~] = size(landingTime_y2);
title(b3Ax,['Infrared LED Tracking (n = ' num2str(numrows) ')'])
% ylim(b3Ax,[0,0.3])
%   shared figure labels
bax=axes(swLandFig_3,'visible','off');
bax.Title.Visible='on';
bax.XLabel.Visible='on';
bax.YLabel.Visible='off';
%ylabel(hax,'Probability');
xlabel(bax,'Duration (s)');
% title(bax,'Software Landing Accuracy with Image Recognition');
sgtitle('Landing Sequence Duration of Two Image Tracking Methods')

clear numrows

%% Analyze Detection Algorithm Range test results
%ignore first row of initial timestamp
detectionRange_array = table2array(detectionRange_table);
[~,numcol]=size(detectionRange_array);
numseries = numcol/2;
detectionRange_max = zeros(1,numseries);
% find last 100% detection point for each trial
for i=1:numseries
    detectionRange_max(i)=detectionRange_array(find(detectionRange_array(:,2*i) == 100, 1, 'last'),2*i-1);
end
clear numcol i

% COMMENT OUT START
% hardcode update for increased IR range, per J. Haun.
detectionRange_max(4)=3.08;
% COMMENT OUT STOP

detectionRangeFig = figure;
dr_plot = bar(diag(detectionRange_max),'stacked','FaceColor',[0, 0.4470, 0.7410]);   % ensures bars have appropriate width
% dr_plot.FaceColor = [0, 0.4470, 0.7410];
drAx = gca;
% figure formatting
xticks(drAx,linspace(1, numseries, numseries))
xticklabels(drAx,{'RGB','April Tag','Frame Difference','Infrared LED'})
xlim(drAx,[0.5 numseries+0.5])
ylabel(drAx,'distance (m)')
title(drAx,'UAV Tracking Range vs Image Tracking Method')
% ylim(ltAx,[30,170])
drText = zeros(1,numel(xticks));
for i = 1:numel(xticks)
    drText(i) = text(i,detectionRange_max(i)+ 0.1,num2str(round(detectionRange_max(i),2)),...
        'HorizontalAlignment', 'center');
end
clear i numseries

% % COMMENT OUT START
% % hardcode update for increased IR range, per J. Haun.
% delete(drText(4))
% text(4,detectionRange_max(4)+ 0.1,num2str(3.08),...
%         'HorizontalAlignment', 'center')
% % COMMENT OUT STOP

%% Analyze Camera Power Consumption test results

% get all camera power consumption accuracy series, excluding NaN
camPower_idle = camPower_table.power_W_;
camPower_idle = camPower_idle(~isnan(camPower_idle));
camPower_active = camPower_table.Power_W_;
camPower_active = camPower_active(~isnan(camPower_active));


% get stats for idle vs. active camera power, mean and CI
camPowerStats = zeros(7,2);

% default CI = 95% (alpha=0.05)
[mean,sigma,meanCI,sigmaCI] = normfit(camPower_idle);
camPowerStats(1:6,1) = [mean sigma meanCI' sigmaCI']';
[mean,sigma,meanCI,sigmaCI] = normfit(camPower_active);
camPowerStats(1:6,2) = [mean sigma meanCI' sigmaCI']';
% include sample size in stats array
[camPowerStats(7,1),~] = size(camPower_idle);
[camPowerStats(7,2),~] = size(camPower_active);

clear mean sigma meanCI sigmaCI

%% Analyze SBC Power Consumption test results

% get all camera power consumption accuracy series, excluding NaN
sbc_idle = sbcPower_table.power_W_;
sbc_idle = sbc_idle(~isnan(sbc_idle));
sbc_active = sbcPower_table.Power_W_;
sbc_active = sbc_active(~isnan(sbc_active));


% get stats for idle vs. active camera power, mean and CI
sbcPowerStats = zeros(7,2);

% default CI = 95% (alpha=0.05)
[mean,sigma,meanCI,sigmaCI] = normfit(sbc_idle);
sbcPowerStats(1:6,1) = [mean sigma meanCI' sigmaCI']';
[mean,sigma,meanCI,sigmaCI] = normfit(sbc_active);
sbcPowerStats(1:6,2) = [mean sigma meanCI' sigmaCI']';
% include sample size in stats array
[sbcPowerStats(7,1),~] = size(sbc_idle);
[sbcPowerStats(7,2),~] = size(sbc_active);

clear mean sigma meanCI sigmaCI
%% Quick stats on hover tests
hoverStats = zeros(7,2);

hover_250 = [244 190 199];
hover_380 = [215];

[mean,sigma,meanCI,sigmaCI] = normfit(hover_250);
hoverStats(1:6,1) = [mean sigma meanCI' sigmaCI']';
[mean,sigma,meanCI,sigmaCI] = normfit(hover_380);
hoverStats(1:6,2) = [mean sigma meanCI' sigmaCI']';
hoverStats(7,1) = numel(hover_250);
hoverStats(7,2) = numel(hover_380);
disp('hoverStats')
disp(hoverStats)

clear mean sigma meanCI sigmaCI

%% Quick stats on mobile tests
mobileStats = zeros(7,1);

mobile_250 = [165 163 116 116];
% mobile_380 = [3.583333333];

[mean,sigma,meanCI,sigmaCI] = normfit(mobile_250);
mobileStats(1:6,1) = [mean sigma meanCI' sigmaCI']';
% [mean,sigma,meanCI,sigmaCI] = normfit(hover_380);
% mobileStats(1:6,2) = [mean sigma meanCI' sigmaCI']';
mobileStats(7,1) = numel(mobile_250);
% mobileStats(7,2) = numel(hover_380);
disp('mobileStats')
disp(mobileStats)
clear mean sigma meanCI sigmaCI

%% save all figures to subfolder (NOTE: must have a local subfolder, ARAV_figures/ )
saveas(latencyFig,[pwd '/ARAV_figures/latencyFig.png']);
saveas(swLandFig_1,[pwd '/ARAV_figures/swLandFig_blind.png']);
saveas(swLandFig_2,[pwd '/ARAV_figures/swLandFig_detection_compare_bar.png']);
saveas(swLandFig_3,[pwd '/ARAV_figures/swLandFig_detection_compare_box.png']);
saveas(landingTimeFig,[pwd '/ARAV_figures/landingTimeFig.png']);
saveas(detectionRangeFig,[pwd '/ARAV_figures/detectionRangeFig.png']);

%%
return
