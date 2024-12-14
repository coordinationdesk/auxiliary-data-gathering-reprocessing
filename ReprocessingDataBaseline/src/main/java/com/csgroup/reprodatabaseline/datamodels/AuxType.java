package com.csgroup.reprodatabaseline.datamodels;

import java.util.ArrayList;
import java.util.List;

import com.csgroup.reprodatabaseline.rules.RuleEnum;


public class AuxType{
	public String LongName;

	public String ShortName;

	public String Format;

	public String Mission;

	public List<String> ProductLevels = new ArrayList<String>();

	public List<String> ProductTypes = new ArrayList<String>();

//	public List<L0ParameterValue> L0ParameterValues = new List<L0ParameterValue>();

	// TODO Add L0Parameters

	public String Variability;

	public String Validity;

	public RuleEnum Rule;

	public String Comments;

	public Boolean usedForProductType(final String productType)
	{
		// First part of ProductType is always the Level of the product to be generated
		final String level = productType.substring(0,2);
		// TODO: Check if second condition should be: ProductLevels.contains(level)
		return ProductTypes.contains(productType) || ( Mission.equals("S3ALL") && ProductTypes.contains(level) );
	}
}


