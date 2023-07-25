$! 3D EVALUATION
$! -------------
$!
$! Defining Symbols for Project AUTOSEG_TRNSFR
$!
$!
$ EVAL_PROJECT_GROUP   :== 0
$ EVAL_PROJECT   :== AUTOSEG_TRNSFR
$ EVAL_PROJECTT  :== AUTOSEG_TRNSFR  !Trim and no spaces etc.
$ EVAL_PROJECTTT :== AUTOSEG_TRNSFR !Trunc to 16
$ EVAL_EVALFILE  :== UE:UCT_EVALUATION_V6.COM
$ EVAL_IPLFILE   :== 
$ EVAL_USERFILE0 :== DISK4:[BONELAB.PROJECTS.IAN.COM]EVAL_AUTOSEG_TRNSFR.COM
$ EVAL_USERFILE1 :== 
$ EVAL_USERFILE2 :== 
$ EVAL_USERFILE3 :== 
$ EVAL_LOGDEST   :== DISK4:[BONELAB.PROJECTS.IAN.LOG]
$ EVAL_LOGFILE   :== .LOG  ! log file appendix
$ EVAL_LOGFILE2  :== DISK4:[BONELAB.PROJECTS.IAN.LOG]EVAL_AUTOSEG_TRNSFR_00000000_00000000.LOG ! full log filename
$ EVAL_EQUEUE    :== SYS$FAST
$ EVAL_PQUEUE    :== 
$ EVAL_COPIES    :== 
$ EVAL_SHEET     :== 
$ EVAL_TYPE      :== 
$ EVAL_SIZE      :== 
$ EVAL_FORMAT    :== 
$ EVAL_COLOR     :== 
$ EVAL_NORM      :== 
$ EVAL_NO_Z      :== 
$ EVAL_SCALE     :== 
$ EVAL_QUALITY   :== 
$!
$ EVAL_DIR       :== DISK4:[BONELAB.PROJECTS.IAN.MODELS]
$ EVAL_FNAME     :== TEST1
$ EVAL_FEXT      :== .ISQ
$ EVAL_FVER      :== 
$ EVAL_STARTFILE :== DISK4:[BONELAB.PROJECTS.IAN.MODELS]TEST1.ISQ
$ EVAL_ISQ       :== 
$ EVAL_ORIG_ISQ  :== DISK4:[BONELAB.PROJECTS.IAN.MODELS]TEST1.ISQ
$ EVAL_AIM       :== DISK4:[BONELAB.PROJECTS.IAN.MODELS]TEST1.AIM
$ EVAL_SEGAIM    :== 
$ EVAL_FNAME0    :== 
$ EVAL_FNAME1    :== 
$ EVAL_FNAME2    :== 
$ EVAL_FNAME3    :== 
$ EVAL_FNAME4    :== 
$ EVAL_FNAME5    :== 
$ EVAL_FNAME6    :== 
$ EVAL_FNAME7    :== 
$ EVAL_FNAME8    :== 
$ EVAL_FNAME9    :== 
$ EVAL_FNAME10   :== 
$ EVAL_FNAME11   :== 
$ EVAL_FNAME12   :== 
$ EVAL_FNAME13   :== 
$ EVAL_FNAME14   :== 
$ EVAL_FNAME15   :== 
$ EVAL_FNAME16   :== 
$!
$ EVAL_PEEL0     :== 
$ EVAL_PEEL1     :== 
$ EVAL_PEEL2     :== 
$ EVAL_PEEL3     :== 
$ EVAL_PEEL4     :== 
$ EVAL_GOBJ0     :== 
$ EVAL_GOBJ1     :== 
$ EVAL_GOBJ2     :== 
$ EVAL_GOBJ3     :== 
$ EVAL_GOBJ4     :== 
$!
$ EVAL_SAMPNAME  :== 
$ EVAL_SAMPNAMET :== _
$ EVAL_SAMPNO    :== 
$ EVAL_MEASNO    :== 
$ EVAL_SITE      :== 
$!
$ EVAL_VOIX     :== 
$ EVAL_VOIY     :== 
$ EVAL_VOIZ     :== 
$ EVAL_VOIDX    :== 
$ EVAL_VOIDY    :== 
$ EVAL_VOIDZ    :== 
$!
$ EVAL_MISC1_0   :== 
$ EVAL_MISC1_1   :== 
$ EVAL_MISC1_2   :== 
$ EVAL_MISC1_3   :== 
$ EVAL_MISC1_4   :== 
$ EVAL_MISC1_5   :== 
$ EVAL_MISC1_6   :== 
$ EVAL_MISC1_7   :== 
$!
$ EVAL_ROTX   :== 
$ EVAL_ROTY   :== 
$ EVAL_ROTZ   :== 
$ EVAL_TX     :== 
$ EVAL_TY     :== 
$ EVAL_TZ     :== 
$ EVAL_SX     :== 
$ EVAL_SY     :== 
$ EVAL_SZ     :== 
$!
$ EVAL_PROBLEM   :== 
$ EVAL_FEPAR_NO  :== 
$ EVAL_FEA0      :== 
$ EVAL_FEA1      :== 
$ EVAL_FEA2      :== 
$ EVAL_FEA3      :== 
$ EVAL_FEA4      :== 
$ EVAL_FEA5      :== 
$ EVAL_FEA6      :== 
$ EVAL_FEA7      :== 
$!
$ EVAL_CALC0   :== 
$ EVAL_CALC1   :== 
$ EVAL_CALC2   :== 
$ EVAL_CALC3   :== 
$ EVAL_CALC4   :== 
$ EVAL_CALC5   :== 
$ EVAL_CALC6   :== 
$ EVAL_CALC7   :== 
$!
$ IPL_IPLFILE   :== 
$ IPL_DIR       :== DISK4:[BONELAB.PROJECTS.IAN.MODELS]
$ IPL_FNAME     :== TEST1
$ IPL_FEXT      :== .ISQ
$ IPL_FVER      :== 
$ IPL_STARTFILE :== DISK4:[BONELAB.PROJECTS.IAN.MODELS]TEST1.ISQ
$ IPL_ORIG_ISQ  :== DISK4:[BONELAB.PROJECTS.IAN.MODELS]TEST1.ISQ
$ IPL_ISQ       :== 
$ IPL_AIM       :== DISK4:[BONELAB.PROJECTS.IAN.MODELS]TEST1.AIM
$ IPL_SEGAIM    :== 
$ IPL_FNAME0    :== 
$ IPL_FNAME1    :== 
$ IPL_FNAME2    :== 
$ IPL_FNAME3    :== 
$ IPL_FNAME4    :== 
$ IPL_FNAME5    :== 
$ IPL_FNAME6    :== 
$ IPL_FNAME7    :== 
$ IPL_FNAME8    :== 
$ IPL_FNAME9    :== 
$ IPL_FNAME10   :== 
$ IPL_FNAME11   :== 
$ IPL_FNAME12   :== 
$ IPL_FNAME13   :== 
$ IPL_FNAME14   :== 
$ IPL_FNAME15   :== 
$ IPL_FNAME16   :== 
$!
$ IPL_PEEL0   :== 
$ IPL_PEEL1   :== 
$ IPL_PEEL2   :== 
$ IPL_PEEL3   :== 
$ IPL_PEEL4   :== 
$ IPL_GOBJ0   :== 
$ IPL_GOBJ1   :== 
$ IPL_GOBJ2   :== 
$ IPL_GOBJ3   :== 
$ IPL_GOBJ4   :== 
$!
$ IPL_SAMPNAME  :== 
$ IPL_SAMPNAMET :== _
$ IPL_SAMPNO   :== 
$ IPL_MEASNO   :== 
$ IPL_SITE     :== 
$!
$ IPL_VOIX     :== 0
$ IPL_VOIY     :== 0
$ IPL_VOIZ     :== 0
$ IPL_VOIDX    :== -1
$ IPL_VOIDY    :== -1
$ IPL_VOIDZ    :== -1
$!
$ IPL_SIGMA0   :== 
$ IPL_SUPPORT0 :== 
$ IPL_LOWER0   :== 
$ IPL_UPPER0   :== 
$ IPL_UNIT0    :== 
$ IPL_SIGMA1   :== 
$ IPL_SUPPORT1 :== 
$ IPL_LOWER1   :== 
$ IPL_UPPER1   :== 
$ IPL_UNIT1    :== 
$ IPL_SIGMA2   :== 
$ IPL_SUPPORT2 :== 
$ IPL_LOWER2   :== 
$ IPL_UPPER2   :== 
$ IPL_UNIT2    :== 
$ IPL_SIGMA3   :== 
$ IPL_SUPPORT3 :== 
$ IPL_LOWER3   :== 
$ IPL_UPPER3   :== 
$ IPL_UNIT3    :== 
$!
$ IPL_MISC1_0  :== 
$ IPL_MISC1_1  :== 
$ IPL_MISC1_2  :== 
$ IPL_MISC1_3  :== 
$ IPL_MISC1_4  :== 
$ IPL_MISC1_5  :== 
$ IPL_MISC1_6  :== 
$ IPL_MISC1_7  :== 
$!
$ IPL_ROTX   :== 
$ IPL_ROTY   :== 
$ IPL_ROTZ   :== 
$ IPL_TX     :== 
$ IPL_TY     :== 
$ IPL_TZ     :== 
$ IPL_SX     :== 
$ IPL_SY     :== 
$ IPL_SZ     :== 
$!
$ IPL_PROBLEM   :== 
$ IPL_FEPAR_NO  :== 
$ IPL_FEA0      :== 
$ IPL_FEA1      :== 
$ IPL_FEA2      :== 
$ IPL_FEA3      :== 
$ IPL_FEA4      :== 
$ IPL_FEA5      :== 
$ IPL_FEA6      :== 
$ IPL_FEA7      :== 
$!
$ IPL_CALC0   :== 
$ IPL_CALC1   :== 
$ IPL_CALC2   :== 
$ IPL_CALC3   :== 
$ IPL_CALC4   :== 
$ IPL_CALC5   :== 
$ IPL_CALC6   :== 
$ IPL_CALC7   :== 
$!
$! Defining entry point for IPL Loops:
$!
$ UCT_EVALUATION_CUSTOM_TARGET:
$!
$!
$! User Procedure 0:
$ TARGET_FILE :== TEST1.AIM
$ FEXT :== .AIM
$ CLIENT_HOSTNAME :== EMILY.UCALGARY.CA
$ CLIENT_USERNAME :== XTREMECT2
$ DATE_FINISHED :== 2023-07-25