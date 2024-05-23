/**
 * Copyright (c) 2020 CS Group
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package com.csgroup.rba.model;

import java.util.List;

import com.csgroup.jpadatasource.annotations.ODataJPAEntity;
import com.csgroup.jpadatasource.annotations.ODataJPAProperty;
import com.sdl.odata.api.edm.annotations.EdmEntity;
import com.sdl.odata.api.edm.annotations.EdmEntitySet;
import com.sdl.odata.api.edm.annotations.EdmNavigationProperty;
import com.sdl.odata.api.edm.annotations.EdmProperty;

/**
 * @author besquis
 */
@EdmEntity(namespace = "OData.RBA", key = "LongName", containerName = "Container")
@EdmEntitySet("AuxTypes")
@ODataJPAEntity(value = "com.csgroup.rba.model.jpa.AuxTypeJPA")
public class AuxType {

	@ODataJPAProperty
    @EdmProperty(name = "LongName", nullable = false)
    private String LongName;
    
	@ODataJPAProperty
    @EdmProperty(name = "ShortName", nullable = false)
    private String ShortName;
    
	@ODataJPAProperty
    @EdmProperty(name = "Format", nullable = false)
    private String Format;
	
	@ODataJPAProperty
    @EdmProperty(name = "Mission", nullable = false)
    private String Mission;
    
	@ODataJPAProperty
	@EdmNavigationProperty(name = "ProductLevels", nullable = false)
    private List<ProductLevel> ProductLevels;
	
	@ODataJPAProperty
	@EdmNavigationProperty(name = "ProductTypes", nullable = false)
    private List<ProductType> ProductTypes;
    
	@ODataJPAProperty
    @EdmProperty(name = "Variability", nullable = false)
    private Variability Variability;
    
	@ODataJPAProperty
    @EdmProperty(name = "Validity", nullable = false)
    private TimeValidity Validity;
	
	@ODataJPAProperty
    @EdmProperty(name = "InProduction", nullable = false)
    private Boolean InProduction;
	
	@ODataJPAProperty
    @EdmProperty(name = "Rule", precision = 3, nullable = false)
    private Rule Rule;
    
	@ODataJPAProperty
    @EdmProperty(name = "Comments", nullable = false)
    private String Comments;
   	
	public AuxType() {
		// TODO Auto-generated constructor stub
	}

	public String getLongName() {
		return LongName;
	}

	public void setLongName(String longName) {
		LongName = longName;
	}

	public String getShortName() {
		return ShortName;
	}

	public void setShortName(String shortName) {
		ShortName = shortName;
	}

	public String getFormat() {
		return Format;
	}

	public void setFormat(String format) {
		Format = format;
	}
		
	public Boolean getInProduction() {
		return InProduction;
	}

	public void setInProduction(Boolean inProduction) {
		InProduction = inProduction;
	}
		
	
	public Variability getVariability() {
		return Variability;
	}

	public void setVariability(Variability variability) {
		Variability = variability;
	}
	
	public TimeValidity getValidity() {
		return Validity;
	}

	public void setValidity(TimeValidity validity) {
		Validity = validity;
	}

	public Rule getRule() {
		return Rule;
	}

	public void setRule(Rule rule) {
		Rule = rule;
	}

	public String getMission() {
		return Mission;
	}

	public void setMission(String mission) {
		Mission = mission;
	}

	
	public List<ProductLevel> getProductLevels() {
		return ProductLevels;
	}

	public void setProductLevels(List<ProductLevel> productLevels) {
		ProductLevels = productLevels;
	}

	public List<ProductType> getProductTypes() {
		return ProductTypes;
	}

	public void setProductTypes(List<ProductType> productTypes) {
		ProductTypes = productTypes;
	}

	public String getComments() {
		return Comments;
	}

	public void setComments(String comments) {
		Comments = comments;
	}	
	
	
   
}
