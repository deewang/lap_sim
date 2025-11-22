function generate_crg_from_csv_v2(csv_path, out_crg, add_plots)
% GENERATE_CRG_FROM_CSV_V2 Build a CRG refline from ordered XY CSV.
%   generate_crg_from_csv_v2(csv_path, out_crg, add_plots)
%   csv_path: path to CSV with Nx2 [x y] in meters (no header preferred)
%   out_crg : output CRG filename (e.g. 'generated_track.crg')
%   add_plots: optional boolean (default true) -> show diagnostics

if nargin < 3, add_plots = true; end

% --- config: adjust to taste ---
uinc = 0.25;          % sampling along reference line in meters (smaller = finer)
v_half = 3.0;         % half-width of road (meters)
vinc = 0.5;           % lateral increment for CRG grid
% spline-fitting options (tune if you under/oversmooth)
opts = struct();
opts.sf_incr = 5;     % spline segmentation increment (try 2..10)
opts.ss_spar = 0.1; % smoothing parameter (0..1; lower = smoother) .005 default. up to .7 for autocross. .1 for endurances.

flipDirection = true;   %depends if python gets direction right.
flipCurvature = true; %by default true to match topview image.

% --- add OpenCRG path if needed (adjust for your install) ---
addpath("C:\Program Files\CRG\standard_download68f854e2a52d2_48292\open-crg\matlab\lib");

%% 1) Read CSV
pxy = readmatrix(csv_path);
if size(pxy,2) < 2
    error('CSV must be Nx2 with x,y columns');
end
pxy = double(pxy(:,1:2)); % Nx2

% Quick check: ordering and spacing
d = sqrt(sum(diff(pxy).^2,2));
fprintf('CSV points: %d, mean spacing: %.3f m\n', size(pxy,1), mean(d));

%% 2) Fit smooth piecewise polynomial (ppxy)
ppxy = crg_gen_pxy2ppxy(pxy, opts);  % uses demo logic; returns pp-form refline

%% 3) Integrate spline -> reference line sampled at uniform uinc
[data, err] = crg_gen_ppxy2phi(ppxy, uinc);

data.z = zeros(length(data.p)+1, 2, 'single');
data.v = single(1);

if flipDirection  % cw to cww
   data = crg_flip(data);
end

%% to apply modifications: open crg_mods() find field that turns on if statement. 
%% set the field to the value and then set data to the output of crg_mods()
if flipCurvature
    data.mods.scrv = -1;
    data = crg_mods(data);
    data=crg_check(data);
end



%% 6) Validate and fix
data = crg_check(data);
if ~isfield(data, 'ok')
    error('CRG check failed');
end

%% 7) Write file (and report)
data.filenm = out_crg;
data.ct{1} = sprintf('refline generated from %s at %s', csv_path, datestr(now));
crg_write(data, out_crg);
fprintf('Wrote CRG: %s\n', out_crg);

crg = crg_show(data)

% Copy the file to chrono demo directory to test
[status, msg] = copyfile(out_crg, "C:\Users\leoni\(LOCAL)PROJECTS\FormulaUBC\track-parsing\dev\chronoSourceCode\chrono\build\chrono-local - Copy\bin\data\vehicle\terrain\crg_roads");

if status
    fprintf('Copied CRG to backup location: %s\n', backup_path);
else
    warning('Failed to copy CRG file: %s\n', msg);
end

end
