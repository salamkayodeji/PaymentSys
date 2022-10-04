const types = document.querySelectorAll("div input[type=radio]");

$(document).ready(function(){
	$(".ajaxLoader").hide();
	// Product Filter Start
	$("#priceFilterBtn").on('click', function(){
		var _minPrice=$('#maxPrice').attr('min');
		var _maxPrice=$('#maxPrice').val();
		var _filterObj={};
		_filterObj.minPrice=_minPrice;
		_filterObj.maxPrice=_maxPrice;

		// Run Ajax
		$.ajax({
			url:'/filter-price',
			data:_filterObj,
			dataType:'json',
			beforeSend:function(){
				$(".ajaxLoader").show();
			},
			success:function(res){
				console.log(res);
				$("#filteredItems").html(res.products);
				$(".ajaxLoader").hide();
			}
		});
	});
	// End

	// Filter Product According to the price
	$("#maxPrice").on('blur',function(){
		var _min=$(this).attr('min');
		var _max=$(this).attr('max');
		var _value=$(this).val();
		console.log(_value,_min,_max);
		if(_value < parseInt(_min) || _value > parseInt(_max)){
			alert('Values should be '+_min+'-'+_max);
			$(this).val(_min);
			$(this).focus();
			$("#rangeInput").val(_min);
			return false;
		}
	});
	// End
});

$(document).ready(function(){
	$(".ajaxLoader").hide();
	// Product Filter Start
	$(".btn-check").on('click',function(){
		var _filterObj={};
		$(".btn-check").each(function(index,ele){
			var _filterVal=$(this).val();
			var _filterKey=$(this).data('filter');
			_filterObj[_filterKey]=Array.from(document.querySelectorAll('input[data-filter='+_filterKey+']:checked')).map(function(el){
			 	return el.value;
			});
		});

		// Run Ajax
		$.ajax({
			url:'/filter-data',
			data:_filterObj,
			dataType:'json',
			beforeSend:function(){
				$(".ajaxLoader").show();
			},
			success:function(res){
				console.log(res);
				$("#filteredProducts").html(res.status);
				$(".ajaxLoader").hide();
			}
		});
	});
	// End

});

var link = document.getElementById('RefSearchBox');
if(link){
RefSearchBox.addEventListener("keyup", (event) => {
	var _search_text = link.value;
	console.log(_search_text)
	var _filterObj = {}
	_filterObj.search_text=_search_text;

	$.ajax({
		url:'/filter-text',
		data:_filterObj,
		dataType:'json',

		beforeSend:function(){
			$(".ajaxLoader").show();
		},
		success:function(res){
			console.log(res);
			$("#filteredProducts").html(res.search_text);
			$(".ajaxLoader").hide();
		}
	});
// End
})};

$(document).ready(function(){
	$(".ajaxLoader").hide();
	// Product Filter Start
types.forEach((radioElement) => {

	radioElement.addEventListener('click',function(event){
		console.log(event.target.value)
		var _filterObj={};
		var number=document.getElementById("total_value");  
		var transaction_id=document.getElementById("transaction_id");  
		_filterObj.card=event.target.value;
		_filterObj.amount = number.value * 100
		_filterObj.transaction_id = transaction_id.value
		console.log(_filterObj)


		// Run Ajax
		$.ajax({
			url:'/card-payment',
			data:_filterObj,
			dataType:'json',
			headers: {'X-CSRFToken': csrftoken},
			method: 'POST',
			beforeSend:function(){
				$(".ajaxLoader").show();
			},
			success:function(res){
				console.log(res);
                window.location.href='{% url "home" %}'
				$(".ajaxLoader").hide();
			}
		});
	});
	// End

})});
