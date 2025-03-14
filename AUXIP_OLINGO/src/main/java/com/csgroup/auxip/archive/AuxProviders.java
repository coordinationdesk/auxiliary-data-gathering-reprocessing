package com.csgroup.auxip.archive;

import java.util.ArrayList;
import java.util.List;

public class AuxProviders {
	
	public static List<String> MPC_CAL = new ArrayList<>(List.of( 
			"AUX_CAL",
			"GIP_",
			"SR_1_CA1LAX",
			"SR_1_CA1SAX",
			"SR_1_CA2KAX",
			"SR_1_CA2CAX",
			"MW_1_NIR_AX",
			"MW_1_DNB_AX",
			"MW_1_MON_AX",
			"AX___DEM_AX",
			"AX___LWM_AX",
			"AX___OOM_AX",
			"AX___CLM_AX",
			"AX___TRM_AX",
			"AX___CST_AX",
			"SR___CHDRAX",
			"SR___CHDNAX",
			"SR_1_CONMAX",
			"SR_1_CONCAX",
			"SR_2_CON_AX",
			"SR___LSM_AX",
			"SR_2_IC01AX",
			"SR_2_IC02AX",
			"SR_2_IC03AX",
			"SR_2_IC04AX",
			"SR_2_IC05AX",
			"SR_2_IC06AX",
			"SR_2_IC07AX",
			"SR_2_IC08AX",
			"SR_2_IC09AX",
			"SR_2_IC10AX",
			"SR_2_EOT1AX",
			"SR_2_EOT2AX",
			"SR_2_LT1_AX",
			"SR_2_LT2_AX",
			"SR_2_LNEQAX",
			"SR_2_GEO_AX",
			"SR_2_MSS1AX",
			"SR_2_MSS2AX",
			"SR_2_ODLEAX",
			"SR_2_WNDLAX",
			"SR_2_WNDSAX",
			"SR_2_SIGLAX",
			"SR_2_SIGSAX",
			"SR_2_SET_AX",
			"SR_2_SSM_AX",
			"SR_2_MSMGAX",
			"SR_2_CP00AX",
			"SR_2_CP06AX",
			"SR_2_CP12AX",
			"SR_2_CP18AX",
			"SR_2_S1AMAX",
			"SR_2_S2AMAX",
			"SR_2_S1PHAX",
			"SR_2_S2PHAX",
			"SR_2_MDT_AX",
			"SR_2_SHD_AX",
			"SR_2_SSBLAX",
			"SR_2_SSBSAX",
			"SR_2_SD01AX",
			"SR_2_SD02AX",
			"SR_2_SD03AX",
			"SR_2_SD04AX",
			"SR_2_SD05AX",
			"SR_2_SD06AX",
			"SR_2_SD07AX",
			"SR_2_SD08AX",
			"SR_2_SD09AX",
			"SR_2_SD10AX",
			"SR_2_SD11AX",
			"SR_2_SD12AX",
			"SR_2_SI01AX",
			"SR_2_SI02AX",
			"SR_2_SI03AX",
			"SR_2_SI04AX",
			"SR_2_SI05AX",
			"SR_2_SI06AX",
			"SR_2_SI07AX",
			"SR_2_SI08AX",
			"SR_2_SI09AX",
			"SR_2_SI10AX",
			"SR_2_SI11AX",
			"SR_2_SI12AX",
			"SR_2_SST_AX",
			"SR_2_LRC_AX",
			"SR_2_SFL_AX",
			"SR_2_FLT_AX",
			"SR_2_RRC_AX",
			"SR_2_CCT_AX",
			"SR_2_SURFAX",
			"SR_2_RET_AX",
			"SR_2_MLM_AX",
			"SR_2_MAG_AX",
			"SR_2_LUTFAX",
			"SR_2_LUTEAX",
			"SR_2_LUTSAX",
			"MW___STD_AX",
			"OL_1_EO__AX",
			"OL_1_RAC_AX",
			"OL_1_SPC_AX",
			"OL_1_CLUTAX",
			"OL_1_INS_AX",
			"OL_1_CAL_AX",
			"OL_1_PRG_AX",
			"OL_2_PCP_AX",
			"OL_2_PPP_AX",
			"OL_2_CLP_AX",
			"OL_2_WVP_AX",
			"OL_2_ACP_AX",
			"OL_2_OCP_AX",
			"OL_2_VGP_AX",
			"SL_1_PCP_AX",
			"SL_1_ANC_AX",
			"SL_1_N_S1AX",
			"SL_1_N_S2AX",
			"SL_1_N_S3AX",
			"SL_1_O_S1AX",
			"SL_1_O_S2AX",
			"SL_1_O_S3AX",
			"SL_1_NAS4AX",
			"SL_1_NAS5AX",
			"SL_1_NAS6AX",
			"SL_1_NBS4AX",
			"SL_1_NBS5AX",
			"SL_1_NBS6AX",
			"SL_1_OAS4AX",
			"SL_1_OAS5AX",
			"SL_1_OAS6AX",
			"SL_1_OBS4AX",
			"SL_1_OBS5AX",
			"SL_1_OBS6AX",
			"SL_1_N_S7AX",
			"SL_1_N_S8AX",
			"SL_1_N_S9AX",
			"SL_1_N_F1AX",
			"SL_1_N_F2AX",
			"SL_1_O_S7AX",
			"SL_1_O_S8AX",
			"SL_1_O_S9AX",
			"SL_1_O_F1AX",
			"SL_1_O_F2AX",
			"SL_1_VIC_AX",
			"SL_1_GEO_AX",
			"SL_1_GEC_AX",
			"SL_1_CLO_AX",
			"SL_1_ESSTAX",
			"SL_2_PCP_AX",
			"SL_2_S6N_AX",
			"SL_2_S7N_AX",
			"SL_2_S8N_AX",
			"SL_2_S9N_AX",
			"SL_2_F1N_AX",
			"SL_2_F2N_AX",
			"SL_2_S7O_AX",
			"SL_2_S8O_AX",
			"SL_2_S9O_AX",
			"SL_2_N2_CAX",
			"SL_2_N3RCAX",
			"SL_2_N3_CAX",
			"SL_2_D2_CAX",
			"SL_2_D3_CAX",
			"SL_2_SST_AX",
			"SL_2_SDI3AX",
			"SL_2_SDI2AX",
			"SL_2_SSESAX",
			"SL_2_LSTCAX",
			"SL_2_LSTBAX",
			"SL_2_LSTVAX",
			"SL_2_LSTWAX",
			"SL_2_LSTEAX",
			"SL_2_FRPTAX",
			"SL_2_SSTAAX",
			"OL_1_PCPBAX",
			"SL_1_PCPBAX",
			"SL_1_PLTBAX",
			"OL_2_PCPBAX",
			"OL_2_PLTBAX",
			"SL_2_PCPBAX",
			"OL_1_MCHDAX",
			"SL_1_MCHDAX",
			"SY_1_PCP_AX",
			"SY_1_CDIBAX",
			"SY_2_PCP_AX",
			"SY_2_PCPSAX",
			"SY_2_RAD_AX",
			"SY_2_RADPAX",
			"SY_2_SPCPAX",
			"SY_2_RADSAX",
			"SY_2_PCPBAX",
			"SY_2_PLTBAX",
			"SY_2_CVPBAX",
			"SY_2_PVPBAX",
			"SY_2_CVSBAX",
			"SY_2_PVSBAX",
			"SY_1_GCPBAX",
			"SL_2_ACLMAX",
			"SL_2_ART_AX",
			"SL_2_OSR_AX",
			"SL_2_PCPAAX",
			"SY_2_ACLMAX",
			"SY_2_ART_AX",
			"SY_2_LSR_AX",
			"SY_2_OSR_AX",
			"SY_2_PCPAAX",
			"SL_2_CFM_AX",
			"SL_2_FXPAAX",
			"SL_2_PCPFAX",
			"SL_2_PLFMAX",
			"SL_2_SXPAAX",
			"SL_1_IRE_AX",
			"SL_1_LCC_AX",
			"SL_1_CDP_AX",
			"SL_1_CLP_AX",
			"SL_1_ADJ_AX",
			"SL_1_RTT_AX",
			"SY_2_AODCAX"
			));
	
	public static List<String> POD = new ArrayList<>(List.of(
			"POEORB",
			"RESATT",
			"AUX_PREORB",
			"AUX_RESORB",
			"SR_2_PMPPAX",
			"SR_2_PCPPAX",
			"SR___POEPAX",
			"SR___MGNPAX",
			"SR___ROE_AX",
			"GN_1_NSA_AX",
			"GN_1_NTR_AX",
			"GN_1_NPR_AX",
			"GN_1_ATX_AX",
			"GN_1_CHD_AX",
			"GN_1_NSA3AX",
			"GN_1_NTR3AX",
			"GN_1_ATX3AX",
			"SR_2_NRPPAX",
			"AX___FPO_AX",
			"AX___FRO_AX"
			));

}
