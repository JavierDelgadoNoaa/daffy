 &time_control
 run_days                            = 0,
 run_hours                           = _RUNH,
 run_minutes                         = 0,
 run_seconds                         = 0,
 start_year                          = _START_YEAR,
 start_month                         = _START_MONTH,
 start_day                           = _START_DAY,
 start_hour                          = _START_HOUR,
 start_minute                        = _START_MINUTE,
 start_second                        = 00,
 end_year                            = _END_YEAR,
 end_month                           = _END_MONTH,
 end_day                             = _END_DAY,
 end_hour                            = _END_HOUR,
 end_minute                          = _END_MINUTE,
 end_second                          = 00,
 interval_seconds                    = _INTERVAL_SECONDS,
 history_interval                    = _HISTORY_INTERVAL,
 frames_per_outfile                  = _FRAMES_PER_OUTFILE,
 analysis                            = F,
 restart                             = .false.,
 restart_interval                    = _RESTART_INTERVAL
 override_restart_timers             = .true. ! required for restart runs to generate wrfout @fhr000 - may cause problem if using fdda and sst
 reset_simulation_start              = .true.,
 tstart                              = 01,
 io_form_input                       = 2
 io_form_history                     = 2
 io_form_restart                     = 2
 io_form_boundary                    = 2
 io_form_auxinput1                   = 2
 write_input                           = .true.
 input_outname                       = "wrf_3dvar_input_d<domain>_<date>"
 input_inname                        = "wrf_3dvar_input_d<domain>_<date>"
 INPUTOUT_INTERVAL                    = _CYCLE_FREQUENCY 
 auxinput1_inname                    = "met_nmm.d<domain>.<date>"
 frames_per_auxhist4                 = 1
 io_form_auxhist4                    = 2
 auxhist4_interval                   = _AUXHIST_INTERVAL
 auxhist4_outname                    = _AUXHIST_FILENAME
 debug_level                         = 1 
 /

 &fdda
 /

 &domains
 time_step                           = _TIMESTEP,
 time_step_fract_num                 = 0,
 time_step_fract_den                 = 1,
 max_dom                             = _MAX_DOM,
 s_we                                = 1,      1,   1,   1,   1,   1,   1,   1,   1,
 e_we                                = _E_WE,
 s_sn                                = 1,      1,   1,   1,   1,   1,   1,   1,   1,
 e_sn                                = _E_SN,
 s_vert                              = 1,      1,   1,   1,   1,   1,   1,   1,   1,  
 e_vert                              = _E_VERT,
 dx                                  = _DX,
 dy                                  = _DY,
 grid_id      =   1,
 tile_sz_x                           = 0,
 tile_sz_y                           = 0,
 numtiles                            = 1,
 nproc_x                             = -1,
 nproc_y                             = -1,
 parent_id                           =  0,   1,   2,   1,   4,   1,   6,   1,   8,
 parent_grid_ratio                   = 1,   3,   3,   3,   3,   3,   3,   3,   3,
 parent_time_step_ratio              = 1,   3,   3,   3,   3,   3,   3,   3,   3,
 i_parent_start                      = _I_PARENT_START
 j_parent_start                      = _J_PARENT_START
 feedback                            = 1,
 num_moves                           = -99
 num_metgrid_levels                  = _NUM_METGRID_LEVELS,
 p_top_requested                     = 200,
 ptsgm                               = 42000
 eta_levels = 1.0, 0.995253,0.990479,0.985679,0.980781,0.975782,0.970684,0.965486,0.960187,0.954689,0.948991,0.943093,0.936895,0.930397,0.923599,0.916402,0.908404,0.899507,0.888811,0.876814,0.862914,0.847114,0.829314,0.809114,0.786714,0.762114,0.735314,0.706714,0.676614,0.645814,0.614214,0.582114,0.549714,0.517114,0.484394,0.451894,0.419694,0.388094,0.356994,0.326694,0.297694,0.270694,0.245894,0.223694,0.203594,0.185494,0.169294,0.154394,0.140494,0.127094,0.114294,0.101894,0.089794,0.078094,0.066594,0.055294,0.044144,0.033054,0.022004,0.010994,0.0,

! movemin was 4 in my previous namelist 
/
 &physics
 num_soil_layers                     =   4,
 mp_physics                          =  85,  85,    
 ra_lw_physics                       =  98,  98,    
 ra_sw_physics                       =  98,  98,  
 sf_sfclay_physics                   =  88,  88, 
 sf_surface_physics                  =  88,  88,   
 bl_pbl_physics                      =   3,  3,  
 cu_physics                          =  84,  0, 
 mommix                              = 1.0,  1.0,   
 h_diff                              = 1.0,  1.0,   
 gwd_opt                             =   0,   0,
 sfenth                              = 0.0, 0.0,
 nrads                               = 240, 720,
 nradl                               = 240, 720, 
 nphs                                =   6,   6,
 ncnvc                               =   6,   6, 
 movemin                             =   6,   6,
 gfs_alpha                           = 0.7, 0.7  ! in prev hwrf: 0.5, 0.5, 
 sas_pgcon                           = 0.2, 0.2, 
 sas_mass_flux                       = 0.5, 0.5, 

 co2tf                               = 1,
! ------------------------------------------------------------------------
!                              VORTEX TRACKER
! ------------------------------------------------------------------------

 vortex_tracker =                     2, 7 ! in prev hwrf: 4, 4




! Options for vortex tracker #4: the revised centroid method:

! Vortex search options:
 vt4_radius                          = 250000.0, 250000.0, 
 vt4_weightexp                       = 1.0,      0.5,      ! weight exponent (1=mass)

! Noise removal options:
 vt4_noise_pmin                      = 85000.,   85000.,   ! min allowed 09LP
 vt4_noise_pmax                      = 103000.,  103000.,  ! max allowed 09LP
 vt4_noise_dpdr                      = 0.6,      0.6,      ! max dP/dx in Pa/m
 vt4_noise_iter                      = 2,        2,        ! noise removal distance
! Disable nest movement at certain intervals to prevent junk in the output files:
 nomove_freq                         = 6.0,      6.0,      ! in hours
 tg_option                           = 1
 ntornado                            = 3, 12
/

 &dynamics
 
  non_hydrostatic                     =.true.,    .true., 
 euler_adv                           = .false.
 wp                                  = 0,        0,  
 coac                                = 3.0,      4.0,
 codamp                              = 6.4,      6.4,
 terrain_smoothing                   = 2,

/

 &bdy_control
 spec_bdy_width                      = 1,
 specified                           = .true. /

 &namelist_quilt 
 poll_servers                        = .true.
 nio_tasks_per_group                 = 4,
 nio_groups                          = 4 /

 &logging
  compute_slaves_silent=.true.
  io_servers_silent=.true.
  stderr_logging=.false.
 /

