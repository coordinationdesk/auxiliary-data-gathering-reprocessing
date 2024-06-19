var debug = true
// TODO: Read from configuration!!
// var urlStart = "http://127.0.0.1:8080" // Local 
var urlStart = "https://auxiliary.copernicus.eu"; 
// "https://dev.reprocessing-preparation.ml" // Dev deployement

var token = null;
var contextData = false;
var urls = {
    "token" : urlStart+"/auth/realms/reprocessing-preparation/protocol/openid-connect/token",
    "reprocessingConfigBaseline" : {
        "auxTypes" : urlStart+"/reprocessing.svc/AuxTypes",
        "auxFiles" : urlStart+"/reprocessing.svc/AuxFiles"
    },
    "reprocessingDataBaseline" : urlStart+"/rdb.svc"
}

var auxiliaryTypes = []
// TODO: Seems not used anymore (pagination is done automatically)
var auxiliaryFilesCount = 341845
var missionReference = []
var productTypesReference = []
var productLevelsReference = []

/**
 * DEBUG : Display console among debug value
 * @param {*} str 
 * @param {*} obj 
 */
var display = function(str,obj) {
    if (debug == true) {
        if (obj) {
            console.log(str,obj)
         } else {
            console.log(str)
        }
    }
}

/**
 * Add a mission reference
 * @param {*} mission 
 * @param {*} auxtype 
 */
var addMissionReference = function(mission,auxtype) {
    if (missionReference[mission] == null) {
        missionReference[mission] = []
    } 
    missionReference[mission][auxtype] = true
}

/**
 * Add a product type
 * @param {*} productType 
 * @param {*} auxtype 
 */
var addProductType = function(productType,auxtype) {
    if (productTypesReference[productType] == null) {
        productTypesReference[productType] = []
    } 
    productTypesReference[productType][auxtype] = true
}

/**
 * Add a product level
 * @param {*} productLevel 
 */
var addProductLevel = function(productLevel) {
    productLevelsReference[productLevel] = true
}

/**
 * Get auxiliary type by name
 * @param {*} name 
 * @returns 
 */
var getAuxTypeByName = function (name) {
    if (auxiliaryTypes == null) {
        auxiliaryTypes = []
        return null
    }
    return auxiliaryTypes[name]
}

/**
 * Add auxiliary type
 * @param {*} name 
 * @param {*} productLevelsArray 
 * @param {*} productLevels 
 * @param {*} productTypesArray 
 * @param {*} productTypes 
 * @param {*} mission 
 */
var updateAuxType = function (name,productLevelsArray,productLevels,productTypesArray,productTypes,mission) {
    var record = getAuxTypeByName(name)
    if (record == null) {
        auxiliaryTypes[name] = {
            productLevelsArray : productLevelsArray,
            productLevels : productLevels,
            productTypesArray  : productTypesArray,
            productTypes  : productTypes,
            mission : mission
        }
    } else {
        if (productLevels != null) {
            record.productLevelsArray = productLevelsArray
            record.productLevels = productLevels,
            mission = mission
        }
        if (productTypes != null) {
            record.productTypesArray = productTypesArray
            record.productTypes = productTypes,
            mission = mission
        }
    }
}

/**
 * Create an internal filter object
 * @param {*} start 
 * @param {*} offset 
 * @param {*} search 
 * @param {*} orderCol 
 * @param {*} orderDir 
 * @param {*} expand 
 * @param {*} from dateTime.min.js
 * @param {*} to 
 * @returns 
 */
var createFilter = function (start, offset, search, orderCol, orderDir,expand,from,to) {
    return {
        "start" : start,
        "offset" : offset,
        "search" : search,
        "order" : {
            "col" : orderCol,
            "dir" : orderDir
        },
        "expand" : expand,
        "from" : from,
        "to" : to
    }
}

/**
 * DEBUG : Create a default filter
 * @returns 
 */
var createDefaultFilter = function () {
    return createFilter(0,10,null,null,null,null)
}

/**
 * Create a filter for Production AUx Types
 * by adding the field for In Production property 
 * @param {*} start 
 * @param {*} offset 
 * @param {*} search 
 * @param {*} orderCol 
 * @param {*} orderDir 
 * @param {*} expand 
 * @param {*} from dateTime.min.js
 * @param {*} to 
 * @returns 
 */
var createProductionFilter = function(start, offset, search, orderCol, orderDir,expand,from,to) {
   console.log("Creating filter to retrieve Aux Types in Production");
   reproFilter = createFilter(start, offset, search, orderCol, orderDir, expand, from, to);
   reproFilter.inProduction = true;
   return reproFilter;
}

/**
 * Add a parameter to url
 * @param {*} data 
 * @param {*} name 
 * @param {*} value 
 * @returns 
 */
var addParam = function(data,name,value) {
    if ( (data == null) || (data.length == 0) ) {
        data += "?"
    } else {
        data += "&"
    }
    data += name + "=" + value
    return data
}

/**
 * Get column name among id (=num)
 * @param {*} id 
 * @returns 
 */
var getColumnName = function(id) {
    switch (id) {
        case 0: return 'Unit'
        case 1: return "ValidityStart"
        case 2: return "ValidityStop"
        case 5: return "AuxType"
        case 6: return "FullName"
        case 7: return "IpfVersion"
        
    }
    return null;
}

/**
 * Get url reprocessing configuration baseline auxtype parameters
 * @param {*} url 
 * @param {*} filter 
 * @returns 
 */
 var getUrlParamsInit = function(url,filter) {

    if (filter == null) {
        return url
    }
    var data = "";
    if (filter.start != null) {
        data = addParam(data,"$skip",filter.start)
    }
    if (filter.offset != null) {
        data = addParam(data,"$top",filter.offset)
    }
    if (filter.expand != null) {
        data = addParam(data,"$expand",filter.expand)
    }
    if (filter.inProduction != null) {
        inprodFilterExpr = "InProduction eq true"
        data = addParam(data,"$filter", inprodFilterExpr)
    }
   
    var completeUrl = url+data
    completeUrl += "&$format=application/json"
    return completeUrl
}

/**
 * Get url reprocessing data baseline parameters
 * @param {*} url 
 * @returns 
 */
var getUrlDataParams = function(url) {
    var data = ""
    // Make search param
    var filterParam = ""

    // Check kind of search
    var id = $('.tab-content .active').attr('id');

    var mission = getMission()
    var unit = getUnitFiltered()
    var productType = getProductTypeFiltered()

    switch (id) {
        case "filter_attribute" :
            names = $("#filter_l0_text").val()
            data = "/getReprocessingDataBaseline(l0_names='"+names+"',mission='"+mission+"',unit='"+unit+"',product_type='"+productType+"')"
            break
        case "filter_period" :
            names = $("#filter_l0_text").val()
            dateStart = moment($('#datepicker_application_from').val(),datePattern).format(dateQueryPattern)+"Z"
            dateStop = moment($('#datepicker_application_to').val(),datePattern).format(dateQueryPattern)+"Z"
            data = "/getReprocessingDataBaseline(start="+dateStart+",stop="+dateStop+",mission='"+mission+"',unit='"+unit+"',product_type='"+productType+"')?$top=10"
            break
            
    }
    return url+data
}

/**
 * Get url reprocessing configuration baseline parameters
 * @param {*} url 
 * @param {*} filter 
 * @returns 
 */
var getUrlParams = function(url,filter) {

    if (filter == null) {
        return url
    }
    var data = "";
    if (filter.start != null) {
        data = addParam(data,"$skip",filter.start)
    }
    if (filter.offset != null) {
        data = addParam(data,"$top",filter.offset)
    }
    if (filter.expand != null) {
        data = addParam(data,"$expand",filter.expand)
    }
    //data = addParam(data, "$count", "true");
    // Make search param
    var filterParam = ""
    if (isDateFilterChecked()) {
        filterParam += "ValidityStart lt "+filter.to+" and ValidityStop gt "+filter.from
    }
    if ((filter.search != null) && (filter.search != "")) {
        if (filterParam != "") {
            filterParam += " and "
        }
        filterParam += "contains(FullName,'"+filter.search+"')"
    }
    // add product type search param
    if (isProductTypeFiltered()) {
        // Filter on product type (and so on mission)
        var productTypeFiltered = getProductTypeFiltered()
        // Do not use filter function because do not work on array of key=>values
        var auxTypesFiltered = []
        Object.keys(auxiliaryTypes).sort().forEach(function(key){
            if (auxiliaryTypes[key].productTypesArray.includes(productTypeFiltered)) {
                // check if in mission
                //console.log("productType",auxiliaryTypes[key])
                if (auxiliaryTypes[key].mission == getMission()) {
                    // get only product type of current mission
                    auxTypesFiltered.push(key)
                } else {
                    // NOP
                    //console.log("nop")
                }
            } else {
                //console.log("not included")
            }
         })
         filtreProduct = "";
         auxTypesFiltered.forEach(function(val) {
            if (filtreProduct != "") {
                filtreProduct += " or "
            }
            filtreProduct += "contains(FullName,'"+val+"')"
        })
        if (filtreProduct != "") {
            if (filterParam != "") {
                filterParam += " and "
            }
            filterParam += "("+filtreProduct+")"
        }
    } else {
        // filter by auxtype of current mission
        display("Filter on current mission",getMission())
        display("auxiliaryTypes",auxiliaryTypes)
        // Do not use filter function because do not work on array of key=>values
        var auxTypesFiltered = []
        Object.keys(auxiliaryTypes).sort().forEach(function(key){
            if (auxiliaryTypes[key].mission == getMission()) {
                // get only product type of current mission
                auxTypesFiltered.push(key)
                //display("get product type "+key+" of mission "+auxiliaryTypes[key].mission,auxiliaryTypes[key])

            } else {
                // NOP
            }
        })
        filtreProduct = "";
        auxTypesFiltered.forEach(function(val) {
            if (filtreProduct != "") {
                filtreProduct += " or "
            }
            filtreProduct += "contains(FullName,'"+val+"')"
        })
        if (filtreProduct != "") {
            if (filterParam != "") {
                filterParam += " and "
            }
            filterParam += "("+filtreProduct+")"
        }

    }
    if (filterParam != "") {
        data = addParam(data,"$filter",filterParam)
    }
    // Make sort param
    if (filter.order.col != null) {
        var orderParam = getColumnName(filter.order.col)
        if (filter.order.dir != null) {
            orderParam += " "+filter.order.dir
        }
        data = addParam(data,"$orderby",orderParam)
    }
    
    var completeUrl = url+data
    completeUrl += "&$format=application/json"
    return completeUrl
}

/**
 * Get Token (promise function)
 * @returns {String} token
 */
var getToken = function() {
    return new Promise((successCallback, failureCallback) => {
        var xhr = new XMLHttpRequest()
        xhr.open("POST", urls.token, true)
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded") // Very important, not application/json
        xhr.onreadystatechange = function () {
            if ( (xhr.readyState === 4 ) && (xhr.status === 200)) {
                var json = JSON.parse(xhr.responseText)
                token = json.access_token
                successCallback(token)
            }
            if ( (xhr.readyState === 4 ) && (xhr.status === 404)) {
                failureCallback(xhr.status)
            }
        };
        //data = "grant_type=password&username=frederic.ligeard@csgroup.eu&password=NsxtxfE96nfGKvR&client_id=reprocessing-preparation"
        data = "grant_type=password&username=copernicus.reprocessing@csgroup.eu&password=DinBKZ2WiDNqyFM&client_id=reprocessing-preparation"
        
        xhr.send(data)
    })
}


/**
 * Get count reprocessing aux files (promise function)
 * @returns 
 */
var getCountReprocessingAuxFiles = function() {
    return new Promise((successCallback, failureCallback) => {
        var xhr = new XMLHttpRequest()
        showLoadingWheel()
        xhr.open("GET", urls.reprocessingConfigBaseline.auxFiles+"/$count", true)
        var bearer="Bearer "+token
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded")
        xhr.setRequestHeader("Authorization", bearer)
        xhr.onreadystatechange = function () {
            if ( (xhr.readyState === 4 ) && (xhr.status === 200)) {
                var response = JSON.parse(xhr.responseText)
                console.log("auxiliaryFilesCount",auxiliaryFilesCount)
                auxiliaryFilesCount = response.value
                hideLoadingWheel()
                successCallback()
            }
            if ( (xhr.readyState === 4 ) && (xhr.status === 404)) {
                hideLoadingWheel()
                failureCallback(xhr.status)
            }
        };
        xhr.send()
    })
}

var getReprocessingAuxFiles = function(filter) {
    return new Promise((successCallback, failureCallback) => {
        var xhr = new XMLHttpRequest()
        xhr.open("GET", getUrlParams(urls.reprocessingConfigBaseline.auxFiles,filter), true)
        var bearer="Bearer "+token
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded")
        xhr.setRequestHeader("Authorization", bearer)
        xhr.onreadystatechange = function () {
            if ( (xhr.readyState === 4 ) && (xhr.status === 200)) {
                var response = JSON.parse(xhr.responseText)
                successCallback( { "filter" : filter,
                                    "response" : response })
            }
            if ( (xhr.readyState === 4 ) && (xhr.status === 0)) {
                failureCallback(xhr.status)
            }
            if ( (xhr.readyState === 4 ) && (xhr.status === 404)) {
                failureCallback(xhr.status)
            }
        };
        xhr.send()
    })
}


/**
 * Get list of aux types (promise function)
 * @param {*} filter 
 * @returns 
 */
 var getReprocessingAuxTypes	 = function(filter) {
    return new Promise((successCallback, failureCallback) => {
        var xhr = new XMLHttpRequest()
        xhr.open("GET", getUrlParamsInit(urls.reprocessingConfigBaseline.auxTypes,filter), true)
        var bearer="Bearer "+token

        // xhr.setRequestHeader("Content-Type", "text/plain")
        xhr.setRequestHeader("Content-Type", "application/json")

        xhr.setRequestHeader("Authorization", bearer)
        xhr.onreadystatechange = function () {
            if ( (xhr.readyState === 4 ) && (xhr.status === 200)) {
                var response = JSON.parse(xhr.responseText)
                successCallback( { 
                    "filter" : filter,
                    "response" : response })
            }
            if ( (xhr.readyState === 4 ) && (xhr.status === 400)) {
                failureCallback(xhr.status)
            }
            if ( (xhr.readyState === 4 ) && (xhr.status === 404)) {
                failureCallback(xhr.status)
            }
        };
        xhr.send()
    })
}


/**
 * Get list of aux types (promise function)
 * @param {*} filter 
 * @returns 
 */
 var getProductionAuxTypes	 = function(filter) {
    return new Promise((successCallback, failureCallback) => {
        var xhr = new XMLHttpRequest()
        xhr.open("GET", getUrlParamsInit(urls.reprocessingConfigBaseline.auxTypes,filter), true)
        var bearer="Bearer "+token

        // xhr.setRequestHeader("Content-Type", "text/plain")
        xhr.setRequestHeader("Content-Type", "application/json")

        xhr.setRequestHeader("Authorization", bearer)
        xhr.onreadystatechange = function () {
            if ( (xhr.readyState === 4 ) && (xhr.status === 200)) {
                var response = JSON.parse(xhr.responseText)
                successCallback( { 
                    "filter" : filter,
                    "response" : response })
            }
            if ( (xhr.readyState === 4 ) && (xhr.status === 400)) {
                failureCallback(xhr.status)
            }
            if ( (xhr.readyState === 4 ) && (xhr.status === 404)) {
                failureCallback(xhr.status)
            }
        };
        xhr.send()
    })
}

/**
 * Get list of data (promise function)
 * @param {*} filter 
 * @returns 
 */
var getReprocessingData = function() {
    return new Promise((successCallback, failureCallback) => {
        var xhr = new XMLHttpRequest()
        var url = getUrlDataParams(urls.reprocessingDataBaseline)
        xhr.open("GET", url, true)
        var bearer="Bearer "+token
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded")
        xhr.setRequestHeader("Authorization", bearer)
        xhr.onreadystatechange = function () {
            if ( (xhr.readyState === 4 ) && (xhr.status === 200)) {
                var response = JSON.parse(xhr.responseText)
                successCallback( { "filter" : null,
                                    "response" : response })
            }
            if ( (xhr.readyState === 4 ) && (xhr.status === 0)) {
                failureCallback(xhr.status)
            }
            if ( (xhr.readyState === 4 ) && (xhr.status === 404)) {
                failureCallback(xhr.status)
            }
        };
        xhr.send()
    })
}

/**
 * Get list of data (promise function)
 * @param {*} filter 
 * @returns 
 */
var downloadAuxipProduct = function(auxipUri) {
    return new Promise((successCallback, failureCallback) => {
        display("Downloading from uri: ", auxipUri);
        var xhr = new XMLHttpRequest();
        // var url = getUrlDataParams(urls.reprocessingDataBaseline)
        xhr.open("GET", auxipUri, true);
        var bearer="Bearer "+token;
		xhr.responseType = "blob";
	xhr.crossDomain = true;
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded")
        xhr.setRequestHeader("Authorization", bearer);
        xhr.onreadystatechange = function () {
		display("Received Response: ", xhr.status);
		display("File to download : ", xhr.response);
		display("ReadyState: : ", xhr.readyState);
            if ( (xhr.readyState === 4 ) && (xhr.status === 200)) {
                var downloadUrl = URL.createObjectURL(xhr.response);
	display("Starting download of ", downloadUrl);
				var a = document.createElement("a");
				document.body.appendChild(a);
				a.style = "display: none";
				a.href = downloadUrl;
				a.download = "";
				a.click();
            }
            if ( (xhr.readyState === 4 ) && (xhr.status === 0)) {
                failureCallback(xhr.status);
            }
            if ( (xhr.readyState === 4 ) && (xhr.status === 404)) {
                failureCallback(xhr.status);
            }
            if ( (xhr.readyState === 4 ) && (xhr.status === 403)) {
                failureCallback(xhr.status);
            }
        };
        xhr.send()
    })
}

/**
 * Manage api call errors
 * @param {*} error 
 */
var manageErrors = function(error) {
    alert('Error '+error);
    console.log("Error",error);
}

/**
 * Update aux types from api response (promise function)
 * @param {*} result 
 * @returns 
 */
var updateAuxTypes = function(result) {
    return new Promise((successCallback, failureCallback) => {
        for (var i=0;i<result.response.value.length;i++) {
            element = result.response.value[i]
            var productLevelArray = null
            var productLevel = null
            var productTypeArray = null
            var productType = null
            if (element.ProductLevels) {
                productLevelArray = element.ProductLevels.map(element => element.Level)
                productLevelArray.forEach( element => addProductLevel(element))
                productLevel = productLevelArray.join(", ")

            }
            if (element.ProductTypes) {
                productTypeArray = element.ProductTypes.map(element => element.Type)
                productTypeArray.forEach( element => addProductType(element,element.ShortName))
                productType = productTypeArray.join(", ")
            }
            updateAuxType(element.ShortName,productLevelArray,productLevel,productTypeArray,productType,element.Mission)
            addMissionReference(element.Mission,element.ShortName)
        }
        successCallback()
    })
}

/**
 * Prefetch all informations needed prior to navigation (promise function)
 * @returns 
 */
var prefetchReprocessingConfigurationBaseline = function() {
    return new Promise((successCallback, failureCallback) => {
        getToken()
        .then(result => prepareAuxTables())
        .then(result => getReprocessingAuxTypes(createFilter(null,null,null,null,null,"ProductLevels")))
        .then(result => updateAuxTypes(result))
        .then(result => getReprocessingAuxTypes(createFilter(null,null,null,null,null,"ProductTypes")))
        .then(result => updateAuxTypes(result))
        .then(result => populateSelects(false))
        //TODO REMOVE.then(result => getCountReprocessingAuxFiles())
        .then(result => initTableReprocessingConfigurationBaseline('table_id') )
        .then(successCallback())
    })
}

/**
 * Prefetch all informations needed prior to navigation (promise function)
 * @returns 
 */
var prefetchProductionConfigurationBaseline = function() {
    console.log("Prefetching Configuration Production Types");
    return new Promise((successCallback, failureCallback) => {
        getToken()
        .then(result => prepareProdAuxTables())
        .then(result => getProductionAuxTypes(createProductionFilter(null,null,null,null,null,"ProductLevels")))
        .then(result => updateAuxTypes(result))
        .then(result => getProductionAuxTypes(createProductionFilter(null,null,null,null,null,"ProductTypes")))
        .then(result => updateAuxTypes(result))
        .then(result => populateSelects(false))
        //TODO REMOVE.then(result => getCountReprocessingAuxFiles())
        .then(result => initTableReprocessingConfigurationBaseline('table_id') )
        .then(successCallback())
    })
}

/**
 * Get product types by mission
 * @param {*} mission 
 * @returns {Array} product types
 */
var getProductTypesByMission = function (mission) {
    var arrayKey = []
    Object.keys(auxiliaryTypes).sort().forEach(function(key){
        if (auxiliaryTypes[key].mission == getMission()) {
            for (var i=0;i<auxiliaryTypes[key].productTypesArray.length;i++) {
                arrayKey[auxiliaryTypes[key].productTypesArray[i]]=auxiliaryTypes[key].productTypesArray[i]
            }
        } else {
            // NOP
        }
    })
    return arrayKey
}

/**
 * Preload all Prod aux tables (promise function)
 * @returns 
 */
var prepareProdAuxTables = function() {
    if ($("#div_allaux_s1_table_id").length == 0) {
        return;
    }
    return new Promise((successCallback, failureCallback) => {
        showDiv("div_allaux_s1_table_id")
        showDiv("div_allaux_s2_table_id")
        showDiv("div_allaux_s3a_table_id")
        showDiv("div_allaux_s3b_table_id")
        
        $("#allaux_s1_table_id").DataTable( {
            dom: '<"toolbar">lBfrtip',
            ajax: 'data/allProdAuxTableS1.txt',
            buttons: [ 'csv' , 'excel' , 'pdf' , 'print' ],
            bLengthChange: false,
            /*oLanguage: {
                sLengthMenu: "Display _MENU_ records&nbsp;&nbsp;"
            }*/
        } )
        
        $("#allaux_s2_table_id").DataTable( {
            dom: '<"toolbar">lBfrtip',
            ajax: "data/allProdAuxTableS2.txt",
            buttons: [ 'csv' , 'excel' , 'pdf' , 'print' ],
            bLengthChange: false,
        } )

        $("#allaux_s3a_table_id").DataTable( {
            dom: '<"toolbar">lBfrtip',
            ajax: "data/allProdAuxTableS3_MWR_SRAL.txt",
            buttons: [ 'csv' , 'excel' , 'pdf' , 'print' ],
            bLengthChange: false,
        } )

        $("#allaux_s3b_table_id").DataTable( {
            dom: '<"toolbar">lBfrtip',
            ajax: "data/allProdAuxTableS3_SLSTR_OLCI_SYN.txt",
            buttons: [ 'csv' , 'excel' , 'pdf' , 'print' ],
            bLengthChange: false,
        } )

        $("div.toolbar").html('Export &nbsp;:&nbsp;');

        successCallback()
    })
}


/**
 * Preload all aux tables (promise function)
 * @returns 
 */
var prepareAuxTables = function() {
    if ($("#div_allaux_s1_table_id").length == 0) {
        return;
    }
    return new Promise((successCallback, failureCallback) => {
        showDiv("div_allaux_s1_table_id")
        showDiv("div_allaux_s2_table_id")
        showDiv("div_allaux_s3a_table_id")
        showDiv("div_allaux_s3b_table_id")
        
        $("#allaux_s1_table_id").DataTable( {
            dom: '<"toolbar">lBfrtip',
            ajax: 'data/allAuxTableS1.txt',
            buttons: [ 'csv' , 'excel' , 'pdf' , 'print' ],
            bLengthChange: false,
            /*oLanguage: {
                sLengthMenu: "Display _MENU_ records&nbsp;&nbsp;"
            }*/
        } )
        
        $("#allaux_s2_table_id").DataTable( {
            dom: '<"toolbar">lBfrtip',
            ajax: "data/allAuxTableS2.txt",
            buttons: [ 'csv' , 'excel' , 'pdf' , 'print' ],
            bLengthChange: false,
        } )

        $("#allaux_s3a_table_id").DataTable( {
            dom: '<"toolbar">lBfrtip',
            ajax: "data/allAuxTableS3_MWR_SRAL.txt",
            buttons: [ 'csv' , 'excel' , 'pdf' , 'print' ],
            bLengthChange: false,
        } )

        $("#allaux_s3b_table_id").DataTable( {
            dom: '<"toolbar">lBfrtip',
            ajax: "data/allAuxTableS3_SLSTR_OLCI_SYN.txt",
            buttons: [ 'csv' , 'excel' , 'pdf' , 'print' ],
            bLengthChange: false,
        } )

        $("div.toolbar").html('Export &nbsp;:&nbsp;');

        successCallback()
    })
}

/**
 * Show all aux tables for a given mission
 * @param {*} mission 
 * @param {*} refresh 
 */
var updateAuxTable = function(mission,refresh = true) {
    if ($("#div_allaux_s1_table_id").length == 0) {
        return;
    }
    hideDiv("div_allaux_s1_table_id")
    hideDiv("div_allaux_s2_table_id")
    hideDiv("div_allaux_s3a_table_id")
    hideDiv("div_allaux_s3b_table_id")
    switch (mission) {
        case "S1SAR" :
            showDiv("div_allaux_s1_table_id")
            if (refresh == true) {
                $("#div_allaux_s1_table_id").DataTable().columns.adjust().draw();
            }
            break
        case "S2MSI" :
            showDiv("div_allaux_s2_table_id")
            if (refresh == true) {
                $("#div_allaux_s2_table_id").DataTable().columns.adjust().draw();
            }
            break
        case "S3ALL" :
            showDiv("div_allaux_s3a_table_id")
            if (refresh == true) {
                $("#div_allaux_s3a_table_id").DataTable().columns.adjust().draw();
            }
            showDiv("div_allaux_s3b_table_id")
            if (refresh == true) {
                $("#div_allaux_s3b_table_id").DataTable().columns.adjust().draw();
            }
            break;
        case "S3MWR" :
        case "S3SRAL" :
            showDiv("div_allaux_s3a_table_id")
            if (refresh == true) {
                $("#div_allaux_s3a_table_id").DataTable().columns.adjust().draw();
            }
            break
        case "S3SLSTR" :
        case "S3OLCI" :
        case "S3SYN" :
            showDiv("div_allaux_s3b_table_id")
            if (refresh == true) {
                $("#div_allaux_s3b_table_id").DataTable().columns.adjust().draw();
            }
            break

    }
}

/**
 * Update select product type
 * @param {*} refresh 
 */
var updateSelectProductType = function(refresh = true) {
    $('#select_product_type').find('option').remove().end()
    if (contextData == false) {
        $('#select_product_type').append($('<option></option>').val("*").text("-- All --")); 
    }
    Object.keys(getProductTypesByMission(getMission())).sort().forEach(function(key){
        $('#select_product_type').append($('<option></option>').val(key).text(key)); 
    })    
    if (contextData == false) {
        updateAuxTable(getMission(),refresh)
    }
    if (refresh != false) {
        updateProductType()    
    }
}

/**
 * Populate selects of mision and product types
 * @param {*} refresh 
 * @returns 
 */
var populateSelects = function(refresh = true) {
    return new Promise((successCallback, failureCallback) => {
        //$('#select_mission').append($('<option></option>').val("*").text("-- All --")); 
        // Display missions list
        Object.keys(missionReference).sort().forEach(function(e, i){
            $('#select_mission').append($('<option></option>').val(e).text(e)); 
         });
        
        // Populate product type list among mission
        updateSelectProductType(refresh)
        $("#select_mission").change(updateSelectProductType)
        if (contextData == false) {
            $("#select_product_type").change(updateProductType)
        }
        successCallback()
    })
}
/**
 * Populate selects of mision and product types
 * ==> WHY ???
 * @param {*} refresh 
 * @returns 
 */
 var populateSelectsData = function(refresh = true) {
    return new Promise((successCallback, failureCallback) => {
        // Populate mission list
        $('#select_mission').append($('<option></option>').val("S1").text("S1"))
        $('#select_mission').append($('<option></option>').val("S2").text("S2"))
        $('#select_mission').append($('<option></option>').val("S3").text("S3"))
        // Populate product type list
        $('#select_product_type').append($('<option></option>').val("SM_RAW").text("S1 / SM_RAW"))
        $('#select_product_type').append($('<option></option>').val("IW_RAW").text("S1 / IW_RAW"))
        $('#select_product_type').append($('<option></option>').val("EW_RAW").text("S1 / EW_RAW")) 
        $('#select_product_type').append($('<option></option>').val("WV_RAW").text("S1 / WV_RAW"))
   
        $('#select_product_type').append($('<option></option>').val("MSI_L0__DS").text("S2 / MSI_L0__DS"))
        $('#select_product_type').append($('<option></option>').val("MSI_L0__GR").text("S2 / MSI_L0__GR"))

        $('#select_product_type').append($('<option></option>').val("MW_0_MWR").text("S3 / MW_0_MWR"))
        $('#select_product_type').append($('<option></option>').val("OL_0_EFR").text("S3 / OL_0_EFR"))
        $('#select_product_type').append($('<option></option>').val("SL_0_SLT").text("S3 / SL_0_SLT"))
        $('#select_product_type').append($('<option></option>').val("SR_0_SRA").text("S3 / SR_0_SRA"))

        successCallback()
    })
}

/**
 * Prefetch reprocessing data baseline informations needed prior to navigation
 * @returns 
 */
var prefetchReprocessingDataBaseline = function() {
    contextData = true
    return new Promise((successCallback, failureCallback) => {
        currentQuery = false
        getToken()
        //.then(result => populateSelectsData(false))
        .then(result => getReprocessingAuxTypes(createFilter(null,null,null,null,null,"ProductLevels")))
        .then(result => updateAuxTypes(result))
        .then(result => getReprocessingAuxTypes(createFilter(null,null,null,null,null,"ProductTypes")))
        .then(result => updateAuxTypes(result))
        .then(result => populateSelects(false))
        .then(result => initTableReprocessingDataBaseline('table_id') )
        .then(successCallback())
    })
}
