jQuery(document).ready(function() {
	var sUsername = jQuery.cookie('tncms-screenname');
	var sAuthToken = jQuery.cookie('tncms-authtoken');
	var sAvatar = jQuery.cookie('tncms-avatarurl');
	if(sUsername){var insertableUserName="<a href=\"/users/profile/"+sUsername.replace(/\+/g," ")+"\">"+sUsername.replace(/\+/g,"&nbsp;")+"</a>";}
	var welcomeMessage = "Welcome back, "+insertableUserName;	

	if ((sAuthToken == null) && (sUsername == null)) {
		jQuery('#post-comment').hide();
		jQuery('#logout-dialog').hide();
		jQuery('#uNavOut').hide();
		jQuery('#uNavReauth').hide();
		jQuery('.not-logged-in').show();
	} else if ((sAuthToken == null) && (sUsername != null)) {
		if(recognizedText!=""){
			welcomeMessage = recognizedText.replace("[USER_NAME]",insertableUserName);
		}
		jQuery('#post-comment').hide();
		jQuery('#logout-dialog').hide();
		jQuery('#uUser').html(welcomeMessage);
		jQuery('#uNavOut').hide();
		jQuery('#uNav').hide();
		jQuery('#uNavReauth').show();
		jQuery('.not-logged-in').show();
	} else {
		if(loggedInText!=""){
			welcomeMessage = loggedInText.replace("[USER_NAME]",insertableUserName);
		}
		jQuery('#login-dialog').hide();
		jQuery('#uUser').html(welcomeMessage);
		jQuery('#uNav').hide();
		jQuery('#uNavOut').show();
		jQuery('#uNavReauth').hide();

		jQuery('#post-comment').show();
		jQuery('.not-logged-in').hide();
		jQuery('.logged-in').show();
	}
	if(sAvatar!=null){
		if(jQuery('#customAvatar').length > 0){ 
			jQuery('#defaultAvatar').hide();
			jQuery('#customAvatar').show();
		}else{
			if(jQuery('#uIcon .custom-avatar').length<1){
				jQuery('#uIcon').append('<img class="custom-avatar" src="'+sAvatar+'" alt="custom avatar"/>');
			}
			jQuery('#defaultAvatar').hide();
		}
	}
	// hide panel until page is loaded
	jQuery('div#blox-user-panel dl').show();
	jQuery('.blox-loading#blox-user-panel').removeClass('blox-loading');
});