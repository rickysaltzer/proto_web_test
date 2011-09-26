$(document).ready(function() {
	$('#tweet_form').hide()

	$('.flashes').hide();
	$('.flashes').slideToggle(duration="fast");
	$('.flashes').fadeOut(duration=5000);

	$('#tweet').click(function() {
		$('#tweet_form').slideToggle();
		$('#tweet_message').focus();
	});

	function ajax_refresh()
	{
		$('#user_tweets').load('/ #user_tweets');
	}

	function ajax_tweet(msg)
	{
		$.ajax({
			type: "POST",
			url: "tweet",
			async: true,
			data: "tweet="+msg,
		});
		$('#tweet').click();
		ajax_refresh();
	}

	var auto_refresh = setInterval(function() {
		ajax_refresh();
	}, 5000);

	$('#tweet_submit').click(function() {
		ajax_tweet($('#tweet_message').val());
		$('#tweet_message').val('')
	});

	$('#tweet_message').keypress(function(e) {
		code = (e.keyCode ? e.keyCode : e.which);
		if ( code == 13 )
		{
			ajax_tweet($('#tweet_message').val());
			$('#tweet_message').val('')
		}
	});
});
