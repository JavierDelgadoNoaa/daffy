&share
 wrf_core = 'NMM',
 max_dom = _MAX_DOM,
 start_date = '_SD',
 end_date = '_ED',
 interval_seconds = _WPS_INTERVAL,
 io_form_geogrid = 2,
/

&geogrid
 parent_id         = 0,1,2,
 parent_grid_ratio = 1,3,3,
 e_we          = _E_WE,
 e_sn          = _E_SN,
 geog_data_res = '2m','2m','2m',
 dx = _DX
 dy = _DY
 map_proj =  'rotated_ll',
 ref_lat   = _HURLAT,
 ref_lon   = _HURLON,
 geog_data_path = '_GEOGRID_DATA_PATH'
 opt_geogrid_tbl_path = './'
 ref_x = 105.0,
 ref_y = 159.0,
/

&ungrib
 out_format = 'WPS',
 prefix = '_WPS_UNGRIB_PREFIX',
/

&metgrid
 fg_name = '_WPS_UNGRIB_PREFIX',
 io_form_metgrid = 2,
 opt_metgrid_tbl_path = './'
/

&mod_levs
 press_pa = 201300 , 200100 , 100000 ,
             95000 ,  90000 ,
             85000 ,  80000 ,
             75000 ,  70000 ,
             65000 ,  60000 ,
             55000 ,  50000 ,
             45000 ,  40000 ,
             35000 ,  30000 ,
             25000 ,  20000 ,
             15000 ,  10000 ,
              5000 ,   1000
 /

