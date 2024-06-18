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
package com.csgroup.rba.model.jpa;

import java.util.ArrayList;
import java.util.List;

import javax.persistence.ElementCollection;
import javax.persistence.Embedded;
import javax.persistence.Entity;
import javax.persistence.EnumType;
import javax.persistence.Enumerated;
import javax.persistence.FetchType;
import javax.persistence.Id;
import javax.persistence.ManyToMany;


/**
 * @author besquis
 */
@Entity(name = "AuxFileTypes")
public class AuxTypeJPA {

    @Id
    private String LongName;
    
    private String ShortName;
    
    private String Format;
    
    private String Origin;
    
    private String Mission;
    private Boolean InProduction;
    
    @ManyToMany
    private List<ProductLevelJPA> ProductLevels;
    
    @ManyToMany
    private List<ProductTypeJPA> ProductTypes;
   

	@Enumerated(EnumType.STRING)
    private VariabilityJPA Variability;
    
	@Enumerated(EnumType.STRING)
	private TimeValidityJPA Validity;
    
    @Enumerated(EnumType.STRING)
    private RuleJPA Rule;
    
    private String Comments;
   	
	public AuxTypeJPA() {
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
	
	public String getOrigin() {
		return Origin;
	}

	public void setOrigin(String origin) {
		Origin = origin;
	}
	

	public Boolean getInProduction() {
		return InProduction;
	}

	public void setInProduction(Boolean inProduction) {
		InProduction = inProduction;
	}
	
	public VariabilityJPA getVariability() {
		return Variability;
	}

	public void setVariability(VariabilityJPA variability) {
		Variability = variability;
	}

	public RuleJPA getRule() {
		return Rule;
	}

	public void setRule(RuleJPA rule) {
		Rule = rule;
	}

	public String getComments() {
		return Comments;
	}

	public void setComments(String description) {
		Comments= description;
	}	

	public TimeValidityJPA getValidity() {
		return Validity;
	}

	public void setValidity(TimeValidityJPA timeValidity) {
		Validity = timeValidity;
	}

	public String getMission() {
		return Mission;
	}

	public void setMission(String mission) {
		Mission = mission;
	}

	public List<ProductLevelJPA> getProductLevels() {
		return ProductLevels;
	}

	public void setProductLevels(List<ProductLevelJPA> productLevels) {
		ProductLevels = productLevels;
	}

	public List<ProductTypeJPA> getProductTypes() {
		return ProductTypes;
	}

	public void setProductTypes(List<ProductTypeJPA> productTypes) {
		ProductTypes = productTypes;
	}
	 
    
	
   
}
