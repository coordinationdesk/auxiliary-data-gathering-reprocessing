/**
 * Copyright (c) 2015 CS Group
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
package com.csgroup.rba.service;

import com.sdl.odata.api.edm.annotations.EdmFunctionImport;
import com.sdl.odata.api.edm.annotations.EdmParameter;

import java.time.ZonedDateTime;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


/**
 * @author besquis
 */
@EdmFunctionImport(function = "GetReproBaselineNamesForPeriodUnBound", includeInServiceDocument = true,
name = "GetReproBaselineNamesForPeriod", namespace = "OData.RBA")
public class GetReproBaselineNamesForPeriodImport {
	private static final Logger LOG = LoggerFactory.getLogger(GetReproBaselineNamesForPeriodImport.class);

	@EdmParameter
    private String Mission;
	
    @EdmParameter
    private String Unit;

    @EdmParameter
    private ZonedDateTime SensingTimeStart;
    
    @EdmParameter
    private ZonedDateTime SensingTimeStop;
    
    @EdmParameter
    private String ProductType;

	public String getUnit() {
		return Unit;
	}

	public void setUnit(String unit) {
		Unit = unit;
	}	

	public ZonedDateTime getSensingTimeStart() {
		return SensingTimeStart;
	}

	public void setSensingTimeStart(ZonedDateTime sensingTimeStart) {
		SensingTimeStart = sensingTimeStart;
	}

	public ZonedDateTime getSensingTimeStop() {
		return SensingTimeStop;
	}

	public void setSensingTimeStop(ZonedDateTime sensingTimeStop) {
		SensingTimeStop = sensingTimeStop;
	}

	public String getProductType() {
		return ProductType;
	}

	public void setProductType(String productType) {
		ProductType = productType;
	}

	public String getMission() {
		return Mission;
	}

	public void setMission(String mission) {
		Mission = mission;
	}

       
}