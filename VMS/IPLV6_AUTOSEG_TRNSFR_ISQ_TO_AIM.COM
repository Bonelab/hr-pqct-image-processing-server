$! Turns ISQ into AIM with selected VOI
$!
$ AIM_NAME := 'IPL_DIR''IPL_FNAME'".AIM"
$ WRITE SYS$OUTPUT "IPL"
$ WRITE SYS$OUTPUT AIM_NAME
$ ON ERROR THEN EXIT 
$ IPL_BATCH 


/isq_to_aim
  -aim_name		origaim
  -isq_filename		"ipl_isq
  -pos			"ipl_voix "ipl_voiy "ipl_voiz
  -dim			"ipl_voidx "ipl_voidy "ipl_voidz

/write_new		
  -name 		origaim
  -filename	        "AIM_NAME
  -compress_type	none 

$ EXIT IPL


