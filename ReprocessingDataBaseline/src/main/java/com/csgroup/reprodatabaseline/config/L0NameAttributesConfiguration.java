/**
 * Copyright (c) 2016 All Rights Reserved by the SDL Group.
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
package com.csgroup.reprodatabaseline.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;

/**
 * The L0 Product Parameters parsing configuration.
 * Configuration specifies for a mission, some of L0 Attributes that can be extracted from the L0 Product name
 *  by specifying the Attribute name, paired to the starting position and the length of the L0 name substring
 * @author Stefano Barone
 */
@Component
@Configuration
@ConfigurationProperties(prefix = "databaseline")
public class L0NameAttributesConfiguration {
	private static final Logger LOG = LoggerFactory.getLogger(L0NameAttributesConfiguration.class);

	private  Map<String, Map<String, SubStringConfig>> missionL0NameAttributesConfiguration = new HashMap<>();

	//@Autowired
	/*
	@Value("#${L0NameParser}")
	public void setMissionL0NameAttributesConfiguration(Map<String, Map<String, SubStringConfig>> missionL0NameAttributesConfiguration) {
		this.missionL0NameAttributesConfiguration = missionL0NameAttributesConfiguration;

	}
	*/

	public L0NameAttributesConfiguration() {
		Map<String, SubStringConfig> s1_configuration = new HashMap<>();
		s1_configuration.put("Polarization", new SubStringConfig(15,2));
		s1_configuration.put("Mode", new SubStringConfig(5,3));
		missionL0NameAttributesConfiguration.put("S1SAR", s1_configuration);
	}

	/**
	 *
	 */
	static public class SubStringConfig {
		private final int startPos;
		private final int numChars;

		SubStringConfig(int start, int len) {
			this.startPos = start;
			this.numChars = len;
		}

		public int getStartPos() {
			return startPos;
		}

		public int getNumChars() {
			return numChars;
		}
	}


	public Map<String, SubStringConfig> getMissionL0NameAttributesConfig(String mission) {
		LOG.debug("Requested configuration for mission "+mission);
		LOG.debug("Configured missions: "+missionL0NameAttributesConfiguration.keySet().toString());
		// TODO: What if mission is not configured?
		return missionL0NameAttributesConfiguration.get(mission);
	}
// TODO Complete TEST
	/**
	 *
	 * @param mission
	 * @param attribute
	 * @return
	 * @throws Exception
	 */
	public SubStringConfig getL0NameAttributeConfig(String mission, String attribute) throws Exception {
		Map<String, SubStringConfig> missionConfig;
		missionConfig = this.getMissionL0NameAttributesConfig(mission);
		// TODO Add check on mission configured
		if (!missionConfig.containsKey(attribute)) {
			String excMessage = String.format("No configuration for L0 Attribute  %s  of mission %s",
					attribute, mission);
			throw new Exception(excMessage);
		}
		return missionConfig.get(attribute);
	}
}
