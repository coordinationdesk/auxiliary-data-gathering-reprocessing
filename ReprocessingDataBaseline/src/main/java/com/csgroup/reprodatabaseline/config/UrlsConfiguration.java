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
import org.springframework.beans.factory.annotation.Value;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;

/**
 * The Archive configuration.
 * @author Esquis Benjamin
 */
@Configuration
@ComponentScan
public class UrlsConfiguration {
    private static final Logger LOG = LoggerFactory.getLogger(UrlsConfiguration.class);
    
    @Value("${urls.reprocessingbaseline}")
    private String reprocessing_baseline_url;
    
    @Value("${urls.auxip}")
    private String auxip_url;

    @Value("${urls.external_auxip}")
    private String external_auxip_url;
	public String getReprocessing_baseline_url() {
		return reprocessing_baseline_url;
	}
	
	public String getAuxip_url() {
		return auxip_url;
	}
    
	public String getExternalAuxip_url() {
		return external_auxip_url;
	}
    
}
