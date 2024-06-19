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
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.convert.DurationUnit;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;

/*
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider;
import software.amazon.awssdk.auth.credentials.AwsSessionCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.auth.signer.AwsS3V4Signer;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.presigner.S3Presigner;
*/

import java.net.URI;
import java.time.Duration;
import java.time.temporal.ChronoUnit;

/**
 * The S3 Wasabi configuration.
 * @author Naceur MESKINI
 */
@Configuration
@ConfigurationProperties(prefix = "quota")
public class QuotasConfiguration {
    private static final Logger LOG = LoggerFactory.getLogger(QuotasConfiguration.class);
   
    @Value("${quota.total_downloads}")
    private int totalDownloadsQuota;

    @Value("${quota.total_downloads_period_in_days}")
    @DurationUnit(ChronoUnit.DAYS)
    private Duration totalDownloadsPeriod;

    @Value("${quota.parallel_downloads}")
    private int parallelDownloadsQuota;

    @Value("${quota.parallel_downloads_deltatime_in_seconds}")
    @DurationUnit(ChronoUnit.SECONDS)
    private Duration parallelDownloadsDeltaTime;

    public Duration getParallelDownloadsDeltaTime() {
        return parallelDownloadsDeltaTime;
    }
    public int getParallelDownloadsQuota() {
        return parallelDownloadsQuota;
    }
    public Duration getTotalDownloadsPeriod() {
        return totalDownloadsPeriod;
    }
    public int getTotalDownloadsQuota() {
        return totalDownloadsQuota;
    }

}
