/* test:01 */
$(function (){
    var rTitle = $('span.blox-headline').text();
    var rSummary = $('#blox-story-text p:first').html();
	/* master share button*/
	var object = SHARETHIS.addEntry({
		title: rTitle,
		summary: rSummary},
		{button:false}
	);
	var element = document.getElementById("share-page");
	object.attachButton(element);
			
	/* master share button hyperlink */
	$("#share-button").click(function(){
		$("#share-page").trigger('click');
		return false;
	})
	/* master print button hyperlink */
	$("#print-button").click(function(){
		$("#print-hardcopy a").trigger('click');
	})

	/* sprite share button */
	$(".share-button-sprite a").click(function(){												
	   $("#share-page").trigger('click');
		var position = $(this).position();
		var topPos = Math.round(position.top - 230) + 'px';
		var leftPos = Math.round(position.left + 20) + 'px';
		$("#stwrapper").css({"top":topPos,left:leftPos});
		return false;
	})

	/* sprite print buttons */
	$(".print-button-sprite a").click(function(){
		$("#print-hardcopy a").trigger('click');
		return false;
	})

	/* sprite text down button */
	$("a.text-down").click(function(){
		$("a#default").trigger('click');
		return false;
	})

	/* sprite text up button */
	$("a.text-up").click(function(){
		$("a#large").trigger('click');
		return false;
	})
});


