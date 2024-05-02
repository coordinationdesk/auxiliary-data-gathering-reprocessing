var maxDisplay = 250
var datePattern = 'D MMM YYYY HH:mm'
var dateQueryPattern = 'YYYY-MM-DDTHH:mm:ss'
var currentFilter = createFilter(null,null,null,null,null,null,null,null)
var currentQuery = false
var dataset = [
                
            ]
/**
 * Show div
 * @param {String} name 
 */
var showDiv = function(name) {
    $("#"+name)[0].style.display = "block"
}

/**
 * Hide div
 * @param {String} name 
 */
var hideDiv = function(name) {
    $("#"+name)[0].style.display = "none"
}

/**
 * Show loading wheel
 */
var showLoadingWheel = function() {
    showDiv("loading")
}

/**
 * Hide loading wheel
 */
var hideLoadingWheel = function() {
    hideDiv("loading")
}


/**
 * Format application period from start to end
 * @param {*} start 
 * @param {*} end 
 * @returns 
 */
var formatApplicationPeriod = function(start,end) {
    return start+"-"+end
}

/**
 * Formate date
 * @param {*} date 
 * @returns 
 */
var formatDate = function(date) {
    var index = date.indexOf("Z")
    var dateFormated = date.substr(0,index)
    return dateFormated
}

/**
 * Formate product levels
 * @param {*} record 
 * @param {*} auxTypeShortName 
 * @returns 
 */
var formatProductLevels = function (record,auxTypeShortName) {
    var auxType = getAuxTypeByName(auxTypeShortName)
    if (auxType == null) {
        return null
    } else {
        return auxType.productLevels
    }
}

/**
 * Formate product types
 * @param {*} record 
 * @param {*} auxTypeShortName 
 * @returns 
 */
var formatProductTypes = function (record,auxTypeShortName) {
    var auxType = getAuxTypeByName(auxTypeShortName)
    if (auxType == null) {
        return null
    } else {
        return auxType.productTypes
    }
}

/**
 * Formate aux filename
 * @param {*} name 
 * @returns 
 */
var formatAuxFileName = function (name) {

    if (name.length>maxDisplay) {
        return name.substring(0,maxDisplay-3)+"..."
    } else {
        return name
    }
}

/**
 * Format lines in AuxFiles table
 * @param {*} result 
 * @returns 
 */
var formatForTableAuxFiles = function(result) {
    return new Promise((successCallback, failureCallback) => {

        var out = []
        for ( var i=0 ; i<result.filter.offset ; i++ ) {
            if ( i < result.response.value.length) {
                var record = result.response.value[i]
                var auxTypeShortName = record.AuxType.ShortName
                out.push( [ 
                    //result.filter.start+i,
                    record.Unit, 
                    //formatApplicationPeriod(record.ValidityStart,record.ValidityStop),
                    formatDate(record.ValidityStart),
                    formatDate(record.ValidityStop),
                    formatProductLevels(record,auxTypeShortName),
                    formatProductTypes(record,auxTypeShortName),
                    auxTypeShortName,
                    formatAuxFileName(record.FullName),
                    record.IpfVersion] );
                }
        }
        var recordCount = auxiliaryFilesCount
        if (result.filter.search.length>0) {
            recordCount = 1000
            showDiv("table_message_id")
        } else {
            hideDiv("table_message_id")
        }
        successCallback({
            "out" : out,
            "recordsTotal" : recordCount,
			"recordsFiltered" : recordCount
        })
    })
}

var formatAuxipLink = function(auxipFile) {
//	return "<a href='"+auxipFile.AuxipLink+"' target='_blank'>"+auxipFile.Name+"</a><br/>"
	return "<a href='#' onclick=onAuxipFileSelected('"+auxipFile.AuxipLink+"');>"+auxipFile.Name+"</a><br/>"
}

/**
 * Format link auxip
 * @param {*} array 
 * @returns 
 */
var formatAuxIpLinks = function (array) {
    res = ""
    array.forEach(element => {
        res += "<a href='"+element.AuxipLink+"' target='_blank'>"+element.Name+"</a><br/>"
    })
    return res
}

/**
 * Format lines in AuxFiles table (with pagination)
 * @param {*} result 
 * @returns 
 */
var formatForTableDataPagination = function(result) {
    return new Promise((successCallback, failureCallback) => {
        var out = []
        var recordCount = result.response.value.length
        for ( var i=result.filter.start ; i<(result.filter.start+result.filter.offset); i++ ) {
            if ( i < result.response.value.length) {
                var record = result.response.value[i]
                out.push( [ 
                    record.Level0,
                    formatAuxIpLinks(record.AuxDataFiles)
                ])
            }
        }
        hideLoadingWheel()
        successCallback({
            "out" : out,
            "recordsTotal" : recordCount,
			"recordsFiltered" : recordCount
        })
    })
}

/**
 * Format table data
 * @param {*} result 
 * @returns 
 */
 // TODO: just return a list of triplets or l0 + pair
 // use map + reduce to build the result dataset
 // resultDataset = result.response.value.map(level0 => { 
 // }
var formatForTableData = function(result) {
    return new Promise((successCallback, failureCallback) => {
        var resultDataset = []
        result.response.value.forEach( level0 => {
            level0.AuxDataFiles.forEach( auxDataFile => {
                resultDataset.push([ level0.Level0, formatAuxipLink(auxDataFile) ])
            })
        })
        successCallback(resultDataset)
    })
}

/**
 * Check if is date filter checked
 * @returns is date filter checked
 */
var isDateFilterChecked = function() {
    if ($("#chk_date_filter")[0]==undefined) {
        return false
    }
    return $("#chk_date_filter")[0].checked
}

/**
 * Check if is product type filtered
 * @returns is product type filtered
 */
var isProductTypeFiltered = function() {
    var value = $("#select_product_type")[0].value
    return ((value != "*") && (value != ''))
}

/**
 * Get unit filtered
 * @returns unit filtered
 */
 var getUnitFiltered = function() {
    return $("#select_unit")[0].value
}


/**
 * Get product type filtered
 * @returns product type filtered
 */
var getProductTypeFiltered = function() {
    return $("#select_product_type")[0].value
}

/**
 * Get mission
 * @returns Mission
 */
var getMission = function() {
    return $("#select_mission")[0].value
}

/**
 * Update filter
 */
var updateDateFilter = function() {
    $('#datepicker_application_from')[0].disabled = isDateFilterChecked()
    $('#datepicker_application_to')[0].disabled = isDateFilterChecked()

    if (isDateFilterChecked()) {
        currentFilter.from = moment($('#datepicker_application_from').val(),datePattern).format(dateQueryPattern)+"Z"
        currentFilter.to = moment($('#datepicker_application_to').val(),datePattern).format(dateQueryPattern)+"Z"
    } else {
        currentFilter.from = null
        currentFilter.to = null
    }
    $('#table_id').DataTable().ajax.reload();
}

/**
 * Update product type
 */
var updateProductType = function() {
    if (contextData == false) {
        $('#table_id').DataTable().ajax.reload();
    }
}

/**
 * Init date time picker
 * @param {*} page 
 */
var initDatePicker = function(page) {
    var currentDate = moment().format(datePattern)
    var nextDate = moment(currentDate, datePattern).add(1, 'J').format(datePattern)

    $('#datepicker_application_from').val(currentDate)
    $('#datepicker_application_to').val(nextDate)

    // TODO TOREMOVE test for rdb
    // $('#datepicker_application_from').val(moment("2019-09-04T00:00:00",dateQueryPattern).format(datePattern))
    // $('#datepicker_application_to').val(moment("2019-09-05T00:00:00",dateQueryPattern).format(datePattern))
    // END TODO TOREMOVE

    new DateTime($('#datepicker_application_from'), {
        format: datePattern,
    })

    new DateTime($('#datepicker_application_to'), {
        format: datePattern,
    })

    if ($('#chk_date_filter').length>0) {
        lc_switch('#chk_date_filter',{
            on_txt: 'On',
            off_txt: 'Off',
            on_color: '#076889',
            compact_mode: false
        })
    
        $('#chk_date_filter')[0].addEventListener('lcs-statuschange', updateDateFilter,page);
    }
}

var onAuxipFileSelected = function(auxipUrl) {
    console.log("URL: ", auxipUrl);
	getToken()
		.then(result => downloadAuxipProduct(auxipUrl));
}

/**
 * Query new data for reprocessing data baseline (from button click)
 */
var queryData = function() {
    // Check if mission if filled
    var mission = getMission()
    var productType = getProductTypeFiltered()
    var unit = getUnitFiltered()

    var datatable = $('#table_id').DataTable()
    showLoadingWheel()
    getReprocessingData()
        .then(result => formatForTableData(result))
        .then(result => {
            datatable.clear()
            datatable.rows.add(result)
            datatable.draw(false)
            hideLoadingWheel()
        })
        .catch(error => {
            console.log("Retry with getToken")
            getToken()
                .then(result => getReprocessingData(currentFilter))
                .then(result => formatForTableData(result))
                .then(result => {
                    datatable.clear()
                    datatable.rows.add(result)
                    datatable.draw(false)
                    hideLoadingWheel()
                })
        })        
	// datatable.on('click', 'td', onAuxipFileSelected);
	// $('#table_id tbody').on( 'click', 'td', function () {
	// 	var cell = datatable.cell( this );
	//	downloadAuxipProduct(cell.data());
	//} );
}

/**
 * Initialize the table Reprocessing Configuration Baseline
 * @param {*} divName 
 * @returns 
 */
var initTableReprocessingConfigurationBaseline = function (divName) {
    return new Promise((successCallback, failureCallback) => {
        $('#'+divName).DataTable( {
            dom: '<"toolbar">lBfrtip',
            buttons: [ 'csv' ,
                       'excel' ,
                       {
                        text: "PDF (A3)",
                        extend: 'pdfHtml5',
                        orientation: 'landscape',
                        pageSize: 'A3'
                       },
                       'print' ],
            serverSide: true,
            ordering: true,
            searching: true,
            processing: true,
            language: {
                'loadingRecords': '&nbsp;',
                'processing': '<div style="vertical-align: middle;height:96px;border-width:1px;border-style:solid;border-color:black;background-color:white"><br><img src="./images/loadingwheel2.gif" height="32px"> Loading</div>',
                'lengthMenu' : 'Display _MENU_ records&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Export :&nbsp;'
            },
            aoColumnDefs: [
                { bSortable: false, "aTargets": [ 3,4 ] }
              ] ,
            ajax: function ( data, callback, settings ) {
                currentFilter.order.col = settings.aaSorting[0][0]
                currentFilter.order.dir = settings.aaSorting[0][1]
                currentFilter = createFilter(settings._iDisplayStart, settings._iDisplayLength,settings.oPreviousSearch.sSearch,currentFilter.order.col,currentFilter.order.dir,"AuxType",currentFilter.from,currentFilter.to)
                getReprocessingAuxFiles(currentFilter)
                    .then(result => formatForTableAuxFiles(result))
                    .then(result => callback( {
                        draw: data.draw,
                        data: result.out,
                        recordsTotal: result.recordsTotal,
                        recordsFiltered: result.recordsFiltered
                    } ))
                    .catch(error => {
                        console.log("Retry with getToken")
                        getToken()
                            .then(result => getReprocessingAuxFiles(currentFilter))
                            .then(result => formatForTableAuxFiles(result))
                            .then(result => callback( {
                                draw: data.draw,
                                data: result.out,
                                recordsTotal: result.recordsTotal,
                                recordsFiltered: result.recordsFiltered
                            }))
                    })
            }
        })
     successCallback()
    })
}

/**
 * (NOT USE FOR THE MOMENT) Initialize the table Reprocessing Data Baseline with pagination (get data each navigation in query)
 * @param {*} divName 
 * @returns 
 */
var initTableReprocessingDataBaselinePagination = function (divName) {
    return new Promise((successCallback, failureCallback) => {
        $('#'+divName).DataTable( {
            serverSide: true,
            ordering: true,
            searching: true,
            language: {
                'loadingRecords': '&nbsp;',
                'processing': '<div class="spinner"></div>'            
            },
            ajax: function ( data, callback, settings ) {
                if (currentQuery == true) {
                    showLoadingWheel()
                    currentFilter = createFilter(settings._iDisplayStart, settings._iDisplayLength,settings.oPreviousSearch.sSearch,currentFilter.order.col,currentFilter.order.dir,"AuxType",currentFilter.from,currentFilter.to)
                    getReprocessingData(currentFilter)
                        .then(result => formatForTableDataPagination(result))
                        .then(result => callback( {
                            draw: data.draw,
                            data: result.out,
                            recordsTotal: result.recordsTotal,
                            recordsFiltered: result.recordsFiltered
                        } ))
                        .then( result => { currentQuery = false })
                        .catch(error => manageErrors(error))
                    }
                }
        } )
        successCallback()
    })
}

/**
 * Initialize the table Reprocessing Data Baseline (get data each query)
 * @param {*} divName 
 * @returns 
 */
var initTableReprocessingDataBaseline = function (divName) {
    return new Promise((successCallback, failureCallback) => {
        $('#'+divName).DataTable( {
            dom: '<"toolbar">lBfrtip',
            buttons: [ 'csv' , 'excel' , 'pdf' , 'print' ],
            processing: true,
            language: {
                'loadingRecords': '&nbsp;',
                'processing': '<div style="vertical-align: middle;height:96px;border-width:1px;border-style:solid;border-color:black;background-color:white"><br><img src="./images/loadingwheel2.gif" height="32px"> Loading</div>'            
            },
            data: dataset
        } );
        $("div.toolbar").html('Export &nbsp;:&nbsp;');
        successCallback()
    })
}
