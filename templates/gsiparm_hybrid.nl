 &SETUP
   miter=2,
   niter(1)=70,
   niter(2)=70,
   write_diag(1)=.true.,
   write_diag(2)=.false.,
   write_diag(3)=.true.,
   gencode=78,
   qoption=2,
   factqmin=0.0,
   factqmax=0.0,
   deltim=15,
   ndat=_NDAT,
   iguess=-1,
   !lwrite_predterms=.true.,
   !reduce_diag=.true.,
   !passive_bc=.false.,
   oneobtest=.false.,
   retrieval=.false.,
   print_diag_pcg=.true.,
   nhr_assimilation=_NHR_ASSIMILATION,
   l_foto=.false.,
   use_pbl=.true.,
   use_compress=.false.,
 /
 &GRIDOPTS
   NLAT=_NLAT,
   NLON=_NLON,
   nsig=_NSIG,
   !hybrid=.false.,
   wrf_nmm_regional=.true.,
   wrf_mass_regional=.false.,
   diagnostic_reg=.true.,
   filled_grid=.true.,
   half_grid=.false.,
   netcdf=.true.,
 /

 &hybrid_ensemble
   l_hyb_ens=.true.,
   uv_hyb_ens=.true.,
   q_hyb_ens=.false., ! (v) option - true to use specific humidity for ens perts, F to use RH
   n_ens=__NUM_MEMBERS__,
   nlon_ens=_NLON,
   nlat_ens=_NLAT,
   beta1_inv=__HYBRID_BETA_VALUE__, ! range:[0,1] - 1 = no ens info ; 0 = no static info
   s_ens_h=__HYBRID_HORIZONTAL_LOCALIZATION__     ! homogeneous isotropic horizontal ensemble localization scale (km)
   s_ens_v=__HYBRID_VERTICAL_LOCALIZATION__ ! in grid points
   pseudo_hybens=__HYBRID_PSEUDO_ENSEMBLE__, ! pseudo-ensemble hybrid for hwrf
   merge_two_grid_ensperts=.false.,   ! If True, merge ens pertubations from two forecast domains to analysis domain (e.g. to use with HWRF moving nests)
   regional_ensemble_option=2 ! wrf nmm
   full_ensemble=.true. ! first ensemble pertubation on first ges instead of ens mean
 /

 &BKGERR
   vs=0.6,
   hzscl=0.2,0.4,0.8,
   bw=0.,
   fstat=.false.,
 /
 &ANBKGERR
   anisotropic=.false.,
   an_vs=1.0,
   ngauss=1,
   an_flen_u=-5.,
   an_flen_t=3.,
   an_flen_z=-200.,
   ifilt_ord=2,
   npass=3,
   normal=-200,
   grid_ratio=4.,
   nord_f2a=4,
 /
 &JCOPTS
 /
 &STRONGOPTS
   !tlnmc_option=0,
   !tlnmc_type=3,  
   !jcstrong=.false.,
   !jcstrong_option=3,
   nstrong=1,
   nvmodes_keep=8,
   period_max=6.,
   period_width=1.5,
   baldiag_full=.false.,
   baldiag_inc=.false.,
 /
 &OBSQC
   dfact=0.75,dfact1=3.0,noiqc=.false.,c_varqc=0.02,vadfile='airsbufr',
 /
 &OBS_INPUT
   dmesh(1)=9.0,dmesh(2)=9.0,dmesh(3)=9.0,dmesh(4)=9.0,dmesh(5)=9,dmesh(6)=120.0,time_window_max=3.0,
   dfile(01)='prepbufr',  dtype(01)='ps',        dplat(01)=' ',         dsis(01)='ps',                  dval(01)=1.0,  dthin(01)=0,
   dfile(02)='prepbufr'   dtype(02)='t',         dplat(02)=' ',         dsis(02)='t',                   dval(02)=1.0,  dthin(02)=0,
   dfile(03)='prepbufr',  dtype(03)='q',         dplat(03)=' ',         dsis(03)='q',                   dval(03)=1.0,  dthin(03)=0,
   dfile(04)='prepbufr',  dtype(04)='pw',        dplat(04)=' ',         dsis(04)='pw',                  dval(04)=1.0,  dthin(04)=0,
   dfile(05)='satwnd',    dtype(05)='uv',        dplat(05)=' ',         dsis(05)='uv',                  dval(05)=1.0,  dthin(05)=0,
   dfile(06)='prepbufr',  dtype(06)='uv',        dplat(06)=' ',         dsis(06)='uv',                  dval(06)=1.0,  dthin(06)=0,
   dfile(07)='prepbufr',  dtype(07)='spd',       dplat(07)=' ',         dsis(07)='spd',                 dval(07)=1.0,  dthin(07)=0,
   dfile(08)='prepbufr',  dtype(08)='dw',        dplat(08)=' ',         dsis(08)='dw',                  dval(08)=1.0,  dthin(08)=0,
   dfile(09)='radarbufr', dtype(09)='rw',        dplat(09)=' ',         dsis(09)='rw',                  dval(09)=1.0,  dthin(09)=0,
   dfile(10)='prepbufr',  dtype(10)='sst',       dplat(10)=' ',         dsis(10)='sst',                 dval(10)=1.0,  dthin(10)=0,
   dfile(11)='gpsrobufr', dtype(11)='gps_ref',   dplat(11)=' ',         dsis(11)='gps',                 dval(11)=1.0,  dthin(11)=0,
   dfile(12)='ssmirrbufr',dtype(12)='pcp_ssmi',  dplat(12)='dmsp',      dsis(12)='pcp_ssmi',            dval(12)=1.0,  dthin(12)=-1,
   dfile(13)='tmirrbufr', dtype(13)='pcp_tmi',   dplat(13)='trmm',      dsis(13)='pcp_tmi',             dval(13)=1.0,  dthin(13)=-1,
   dfile(14)='sbuvbufr',  dtype(14)='sbuv2',     dplat(14)='n16',       dsis(14)='sbuv8_n16',           dval(14)=1.0,  dthin(14)=0,
   dfile(15)='sbuvbufr',  dtype(15)='sbuv2',     dplat(15)='n17',       dsis(15)='sbuv8_n17',           dval(15)=1.0,  dthin(15)=0,
   dfile(16)='sbuvbufr',  dtype(16)='sbuv2',     dplat(16)='n18',       dsis(16)='sbuv8_n18',           dval(16)=1.0,  dthin(16)=0,
   dfile(17)='omibufr',   dtype(17)='omi',       dplat(17)='aura',      dsis(17)='omi_aura',            dval(17)=1.0,  dthin(17)=6,
   dfile(18)='hirs3bufr', dtype(18)='hirs3',     dplat(18)='n16',       dsis(18)='hirs3_n16',           dval(18)=0.0,  dthin(18)=1,
   dfile(19)='hirs3bufr', dtype(19)='hirs3',     dplat(19)='n17',       dsis(19)='hirs3_n17',           dval(19)=6.0,  dthin(19)=1,
   dfile(20)='hirs4bufr', dtype(20)='hirs4',     dplat(20)='n18',       dsis(20)='hirs4_n18',           dval(20)=0.0,  dthin(20)=1,
   dfile(21)='hirs4bufr', dtype(21)='hirs4',     dplat(21)='metop-a',   dsis(21)='hirs4_metop-a',       dval(21)=6.0,  dthin(21)=1,
   dfile(22)='gsndrbufr', dtype(22)='sndr',      dplat(22)='g11',       dsis(22)='sndr_g11',            dval(22)=0.0,  dthin(22)=1,
   dfile(23)='gsndrbufr', dtype(23)='sndr',      dplat(23)='g12',       dsis(23)='sndr_g12',            dval(23)=0.0,  dthin(23)=1,
   dfile(24)='gimgrbufr', dtype(24)='goes_img',  dplat(24)='g11',       dsis(24)='imgr_g11',            dval(24)=0.0,  dthin(24)=1,
   dfile(25)='gimgrbufr', dtype(25)='goes_img',  dplat(25)='g12',       dsis(25)='imgr_g12',            dval(25)=0.0,  dthin(25)=1,
   dfile(26)='airsbufr',  dtype(26)='airs',      dplat(26)='aqua',      dsis(26)='airs281SUBSET_aqua',  dval(26)=1.0, dthin(26)=6,
   dfile(27)='msubufr',   dtype(27)='msu',       dplat(27)='n14',       dsis(27)='msu_n14',             dval(27)=2.0,  dthin(27)=2,
   dfile(28)='amsuabufr', dtype(28)='amsua',     dplat(28)='n15',       dsis(28)='amsua_n15',           dval(28)=10.0, dthin(28)=2,
   dfile(29)='amsuabufr', dtype(29)='amsua',     dplat(29)='n16',       dsis(29)='amsua_n16',           dval(29)=0.0,  dthin(29)=2,
   dfile(30)='amsuabufr', dtype(30)='amsua',     dplat(30)='n17',       dsis(30)='amsua_n17',           dval(30)=0.0,  dthin(30)=2,
   dfile(31)='amsuabufr', dtype(31)='amsua',     dplat(31)='n18',       dsis(31)='amsua_n18',           dval(31)=10.0, dthin(31)=2,
   dfile(32)='amsuabufr', dtype(32)='amsua',     dplat(32)='metop-a',   dsis(32)='amsua_metop-a',       dval(32)=10.0, dthin(32)=2,
   dfile(33)='airsbufr',  dtype(33)='amsua',     dplat(33)='aqua',      dsis(33)='amsua_aqua',          dval(33)=5.0,  dthin(33)=2,
   dfile(34)='amsubbufr', dtype(34)='amsub',     dplat(34)='n15',       dsis(34)='amsub_n15',           dval(34)=3.0,  dthin(34)=3,
   dfile(35)='amsubbufr', dtype(35)='amsub',     dplat(35)='n16',       dsis(35)='amsub_n16',           dval(35)=3.0,  dthin(35)=3,
   dfile(36)='amsubbufr', dtype(36)='amsub',     dplat(36)='n17',       dsis(36)='amsub_n17',           dval(36)=3.0,  dthin(36)=3,
   dfile(37)='mhsbufr',   dtype(37)='mhs',       dplat(37)='n18',       dsis(37)='mhs_n18',             dval(37)=3.0,  dthin(37)=3,
   dfile(38)='mhsbufr',   dtype(38)='mhs',       dplat(38)='metop-a',   dsis(38)='mhs_metop-a',         dval(38)=3.0,  dthin(38)=3,
   dfile(39)='ssmitbufr', dtype(39)='ssmi',      dplat(39)='f13',       dsis(39)='ssmi_f13',            dval(39)=0.0,  dthin(39)=4,
   dfile(40)='ssmitbufr', dtype(40)='ssmi',      dplat(40)='f14',       dsis(40)='ssmi_f14',            dval(40)=0.0,  dthin(40)=4,
   dfile(41)='ssmitbufr', dtype(41)='ssmi',      dplat(41)='f15',       dsis(41)='ssmi_f15',            dval(41)=0.0,  dthin(41)=4,
   dfile(42)='amsrebufr', dtype(42)='amsre_low', dplat(42)='aqua',      dsis(42)='amsre_aqua',          dval(42)=0.0,  dthin(42)=4,
   dfile(43)='amsrebufr', dtype(43)='amsre_mid', dplat(43)='aqua',      dsis(43)='amsre_aqua',          dval(43)=0.0,  dthin(43)=4,
   dfile(44)='amsrebufr', dtype(44)='amsre_hig', dplat(44)='aqua',      dsis(44)='amsre_aqua',          dval(44)=0.0,  dthin(44)=4,
   dfile(45)='ssmisbufr', dtype(45)='ssmis',     dplat(45)='f16',       dsis(45)='ssmis_f16',           dval(45)=0.0,  dthin(45)=4,
   dfile(46)='gsnd1bufr', dtype(46)='sndrd1',    dplat(46)='g12',       dsis(46)='sndrD1_g12',          dval(46)=1.5,  dthin(46)=5,
   dfile(47)='gsnd1bufr', dtype(47)='sndrd2',    dplat(47)='g12',       dsis(47)='sndrD2_g12',          dval(47)=1.5,  dthin(47)=5,
   dfile(48)='gsnd1bufr', dtype(48)='sndrd3',    dplat(48)='g12',       dsis(48)='sndrD3_g12',          dval(48)=1.5,  dthin(48)=5,
   dfile(49)='gsnd1bufr', dtype(49)='sndrd4',    dplat(49)='g12',       dsis(49)='sndrD4_g12',          dval(49)=1.5,  dthin(49)=5,
   dfile(50)='gsnd1bufr', dtype(50)='sndrd1',    dplat(50)='g11',       dsis(50)='sndrD1_g11',          dval(50)=1.5,  dthin(50)=5,
   dfile(51)='gsnd1bufr', dtype(51)='sndrd2',    dplat(51)='g11',       dsis(51)='sndrD2_g11',          dval(51)=1.5,  dthin(51)=5,
   dfile(52)='gsnd1bufr', dtype(52)='sndrd3',    dplat(52)='g11',       dsis(52)='sndrD3_g11',          dval(52)=1.5,  dthin(52)=5,
   dfile(53)='gsnd1bufr', dtype(53)='sndrd4',    dplat(53)='g11',       dsis(53)='sndrD4_g11',          dval(53)=1.5,  dthin(53)=5,
   dfile(54)='gsnd1bufr', dtype(54)='sndrd1',    dplat(54)='g13',       dsis(54)='sndrD1_g13',          dval(54)=1.5,  dthin(54)=5,
   dfile(55)='gsnd1bufr', dtype(55)='sndrd2',    dplat(55)='g13',       dsis(55)='sndrD2_g13',          dval(55)=1.5,  dthin(55)=5,
   dfile(56)='gsnd1bufr', dtype(56)='sndrd3',    dplat(56)='g13',       dsis(56)='sndrD3_g13',          dval(56)=1.5,  dthin(56)=5,
   dfile(57)='gsnd1bufr', dtype(57)='sndrd4',    dplat(57)='g13',       dsis(57)='sndrD4_g13',          dval(57)=1.5,  dthin(57)=5,
   dfile(58)='iasibufr',  dtype(58)='iasi',      dplat(58)='metop-a',   dsis(58)='iasi586_metop-a',     dval(58)=20.0, dthin(58)=1,
   dfile(59)='gomebufr',  dtype(59)='gome',      dplat(59)='metop-a',   dsis(59)='gome_metop-a',        dval(59)=1.0,  dthin(59)=6,
   dfile(60)='sbuvbufr',  dtype(60)='sbuv2',     dplat(60)='n19',       dsis(60)='sbuv8_n19',           dval(60)=1.0,  dthin(60)=0,
   dfile(61)='hirs4bufr', dtype(61)='hirs4',     dplat(61)='n19',       dsis(61)='hirs4_n19',           dval(61)=6.0,  dthin(61)=1,
   dfile(62)='amsuabufr', dtype(62)='amsua',     dplat(62)='n19',       dsis(62)='amsua_n19',           dval(62)=10.0, dthin(62)=2,
   dfile(63)='mhsbufr',   dtype(63)='mhs',       dplat(63)='n19',       dsis(63)='mhs_n19',             dval(63)=3.0,  dthin(63)=3,
   dfile(64)='tcvitl'     dtype(64)='tcp',       dplat(64)=' ',         dsis(64)='tcp',                 dval(64)=1.0,  dthin(64)=0,
   dfile(65)='mlsbufr',   dtype(65)='mls',       dplat(65)='aura',      dsis(65)='mls_aura',            dval(65)=1.0,  dthin(65)=0,
   dfile(66)='seviribufr',dtype(66)='seviri',    dplat(66)='m08',       dsis(66)='seviri_m08',          dval(66)=0.0,  dthin(66)=1,
   dfile(67)='seviribufr',dtype(67)='seviri',    dplat(67)='m09',       dsis(67)='seviri_m09',          dval(67)=0.0,  dthin(67)=1,
   dfile(68)='seviribufr',dtype(68)='seviri',    dplat(68)='m10',       dsis(68)='seviri_m10',          dval(68)=0.0,  dthin(68)=1,
   dfile(69)='hirs4bufr', dtype(69)='hirs4',     dplat(69)='metop-b',   dsis(69)='hirs4_metop-b',       dval(69)=0.0,  dthin(69)=1,
   dfile(70)='amsuabufr', dtype(70)='amsua',     dplat(70)='metop-b',   dsis(70)='amsua_metop-b',       dval(70)=0.0,  dthin(70)=1,
   dfile(71)='mhsbufr',   dtype(71)='mhs',       dplat(71)='metop-b',   dsis(71)='mhs_metop-b',         dval(71)=0.0,  dthin(71)=1,
   dfile(72)='iasibufr',  dtype(72)='iasi',      dplat(72)='metop-b',   dsis(72)='iasi616_metop-b',     dval(72)=0.0,  dthin(72)=1,
   dfile(73)='gomebufr',  dtype(73)='gome',      dplat(73)='metop-b',   dsis(73)='gome_metop-b',        dval(73)=0.0,  dthin(73)=1,
   dfile(74)='atmsbufr',  dtype(74)='atms',      dplat(74)='npp',       dsis(74)='atms_npp',            dval(74)=0.0,  dthin(74)=1,
   dfile(75)='crisbufr',  dtype(75)='cris',      dplat(75)='npp',       dsis(75)='cris_npp',            dval(75)=0.0,  dthin(75)=1,
   dfile(76)='modisbufr', dtype(76)='aodmodis',  dplat(76)='aqua',      dsis(76)='modis_aqua',          dval(76)=1.0,  dthin(65)=6,
   dfile(77)='modisbufr', dtype(77)='aodmodis',  dplat(77)='terra',     dsis(77)='modis_terra',         dval(77)=1.0,  dthin(77)=6,
   dfile(78)='dwbufr',  dtype(78)='dw',        dplat(78)=' ',       dsis(78)='dw',              dval(78)=0.0,  dthin(78)=0, 
 /
 &SUPEROB_RADAR
 /
 &LAG_DATA
 /
 &HYBRID_ENSEMBLE
 /
 &RAPIDREFRESH_CLDSURF
 /
 &CHEM
 /
 &SINGLEOB_TEST
 /

