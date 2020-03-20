% EMCCD Detector Simulation.
%
% S Miller and B Nemati - UAH - 21-Feb-2020
clear; close all; clc; format compact;
addpath('../emccd_detect_m');
addpath('../emccd_detect_m/util');
jMon = 2; fsz = 450*[1,1.3];
scrSize = get(0, 'MonitorPositions'); [nMon,~]=size(scrSize); iMon = min(jMon, nMon);
nr = round(scrSize(iMon,4)/fsz(1)); nc = round(scrSize(iMon,3)/fsz(2)); clear('jMon', 'nMon','fsz');

% Input fluxmap
npix_across = 2000;
flux = 0.07;  % photns/pix/s
fluxmap = flux * ones(npix_across);

studyCase = 'old'
tic
% Simulation inputs
frameTime = 1.;  % Frame time (seconds)
em_gain = 6000.;  % CCD EM gain (e-/photon)
full_well_image  = 60000.;  % Image area full well capacity (e-)
full_well_serial = 90000.;  % Serial (gain) register full well capacity (e-)
dark_current = 0.00028;  % Dark  current rate (e-/pix/s)
cic =  0.02;  % Clock induced charge (e-/pix/frame)
read_noise = 100.;  % Read noise (e-/pix/frame)
bias = 0.;  % Bias offset (e-)
qe = 1.;  % Quantum effiency
cr_rate = 0.;  % Cosmic ray rate (5 for L2) (hits/cm^2/s)
pixel_pitch = 13e-6;  % Distance between pixel centers (m)

zeroFrame = zeros(size(fluxmap)); %#ok<*NOPTS>
npts = 55;
pc_thresh = linspace(200, 1200, npts);
for ithr = 1:npts
    
    % Threshold and photon count
    
    nthr(ithr) = pc_thresh(ithr) / read_noise;
    
    eps_thr(ithr) = exp(- pc_thresh(ithr) / em_gain);
    
    %  dark frame
    if strcmp( studyCase, 'new' )
        darkFrame = emccd_detect_new(zeroFrame, frameTime, em_gain, full_well_image,...
            full_well_serial, dark_current, cic, read_noise, bias,...
            qe, cr_rate, pixel_pitch, true);
    else
        darkFrame = emccd_detect(zeroFrame, frameTime, em_gain, full_well_image,...
            full_well_serial, dark_current, cic, read_noise, bias,...
            qe, cr_rate, pixel_pitch, true);
    end
    dark_an_mn(ithr) = mean(darkFrame(:));
    % photon-count the dark frame
    dark_PC = zeroFrame;
    dark_PC(darkFrame > pc_thresh(ithr)) = 1;
    % the raw photon-counted frame needs to be corrected for inefficiencies 
    % from thresholding and coincidence losses
    % observed mean rate after photon counting 
    nobs_dk(ithr) = nnz(dark_PC) / npix_across^2;
    lambda_dk = -log(1-(nobs_dk(ithr)/eps_thr(ithr)));
    rtrue_dk(ithr) = lambda_dk / frameTime;
    
    % bright frame
    if strcmp( studyCase, 'new' )
        brightFrame = emccd_detect_new(fluxmap, frameTime, em_gain, full_well_image,...
            full_well_serial, dark_current, cic, read_noise, bias,...
            qe, cr_rate, pixel_pitch, true);
    else
        brightFrame = emccd_detect(fluxmap, frameTime, em_gain, full_well_image,...
            full_well_serial, dark_current, cic, read_noise, bias,...
            qe, cr_rate, pixel_pitch, true);
    end
    bright_an_mn(ithr) = mean(brightFrame(:));
    bright_PC = zeroFrame;
    bright_PC(brightFrame > pc_thresh(ithr)) = 1;
    % the raw photon-counted frame needs to be corrected for inefficiencies 
    % from thresholding and coincidence losses
    % observed mean rate after photon counting 
    nobs_br(ithr) = nnz(bright_PC) / npix_across^2;     %#ok<*SAGROW>
    lambda_br = -log(1-(nobs_br(ithr)/eps_thr(ithr)));
    rtrue_br(ithr) = lambda_br / frameTime;

    % photo-electron rate
    r_phe(ithr) = rtrue_br(ithr) - rtrue_dk(ithr);
    
    if ithr ==1
        figure, imagesc(bright_PC); colorbar; colormap gray;
        figure;
        imagesc(brightFrame); %, [0, 2*em_gain*flux*qe*frameTime]
        colorbar;
    end
    
end

%%
figure
plot(nthr, nobs_br/frameTime, nthr, r_phe,  nthr, flux*ones(1, npts))
grid
legend('Observed', 'Corrected', 'Actual')
xlabel('threshold factor')
ylabel('rates, e/pix/s')
title(['RN=',num2str(read_noise),' emG=',num2str(em_gain),' FWCs=',num2str(full_well_serial/1000),'k']);
figure
plot(nthr, eps_thr)
grid
xlabel('threshold factor')
ylabel('threshold effeciency')
title('Assuming all pixels are 1 or 0 real ph-e''s')
toc
autoArrangeFigures(nr, nc, iMon); return;
return