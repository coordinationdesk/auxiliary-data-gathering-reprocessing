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
package com.csgroup.auxip.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;

import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider;
import software.amazon.awssdk.auth.credentials.AwsSessionCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.auth.signer.AwsS3V4Signer;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.presigner.S3Presigner;
import software.amazon.awssdk.services.s3.S3Configuration;

import java.net.URI;

/**
 * The S3 Wasabi configuration.
 * @author Naceur MESKINI
 */
@Configuration
@ComponentScan
public class S3WasabiConfiguration {
    private static final Logger LOG = LoggerFactory.getLogger(S3WasabiConfiguration.class);

    @Value("${s3.access_key}")
    private String accessKey;

    @Value("${s3.secret_key}")
    private String secretAccessKey;

    @Value("${s3.endpoint}")
    private String endPoint; 

    public String getEndPoint() {
	return this.endPoint;
    }

    @Bean
    public S3Presigner s3Presigner() {

	LOG.debug("s3.access_key: "+this.accessKey);
	LOG.debug("s3.secret_key: "+this.secretAccessKey);
        //Region region = Region.EU_CENTRAL_1;
        Region region = Region.of("waw2-1");

        // final String END_POINT = "https://s3.eu-central-1.wasabisys.com";
        String END_POINT =  this.getEndPoint(); // "https://s3.waw2-1.cloudferro.com"; //  
        AwsCredentialsProvider credentialsProvider = StaticCredentialsProvider.create(AwsBasicCredentials.create(this.accessKey, this.secretAccessKey));
        
        return S3Presigner.builder()
        .credentialsProvider(credentialsProvider)
        .endpointOverride(URI.create(END_POINT))
        .serviceConfiguration(S3Configuration.builder()
				.pathStyleAccessEnabled(true)
				.checksumValidationEnabled(false)
				.build())
        .region(region).build();
        //.build(); 

    }
}

