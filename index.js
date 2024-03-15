'use strict';

var libQ = require('kew');
var fs=require('fs-extra');
var config = new (require('v-conf'))();
var exec = require('child_process').exec;
var execSync = require('child_process').execSync;
var spawn = require('child_process').spawn;
var sync = require('child_process').spawnSync;
var json = require('json');
var stringify = require('json-stringify');


module.exports = audiotop;
function audiotop(context) {
	var self = this;

	this.context = context;
	this.commandRouter = this.context.coreCommand;
	this.logger = this.context.logger;
	this.configManager = this.context.configManager;

}

// Tell Volumio that the settings are saved in a file called config.json
audiotop.prototype.getConfigurationFiles = function()
{
	return ['config.json'];
}

audiotop.prototype.onVolumioStart = function()
{
	var self = this;
	var configFile=this.commandRouter.pluginManager.getConfigurationFile(this.context,'config.json');
	this.config = new (require('v-conf'))();
	this.config.loadFile(configFile);

    return libQ.resolve();
}

// Tell Volumio what to do when the plugin gets enabled
audiotop.prototype.onStart = function() {
    var self = this;
    var defer=libQ.defer();

    spawn('/usr/bin/killall', ['audiotop.py'], {
    		detached: true
    });
    // Wait some time for '/usr/bin/killall' to complete
    var waitTimestamp = new Date(new Date().getTime() + 2000);
    while(waitTimestamp > new Date()){};
 
    spawn('/data/plugins/user_interface/audiotop/audiotop.py', {
      detached: true
    });

    //  Once the Plugin has successfull started resolve the promise
    defer.resolve();

    return defer.promise;
};

// Tell Volumio what to do when the plugin gets disabled
audiotop.prototype.onStop = function() {
    var self = this;
    var defer=libQ.defer();
    // Use spawn with option 'detached: true' to run a command. 'detached: false' will crash Volumio instantly, because 'child process /usr/bin/killall' exited.
    spawn('/usr/bin/killall', ['audiotop.py'], {
    		detached: true
    });

    // Once the Plugin has successfull stopped resolve the promise
    defer.resolve();

    return libQ.resolve();
};

audiotop.prototype.onRestart = function() {
    var self = this;
    restartAudiotop();
    // Use this if you need it
};



function restartAudiotop() {

    spawn('/usr/bin/killall', ['audiotop.py'], {
    	detached: true
    });
    // Wait some time for '/usr/bin/killall' to complete
    var waitTimestamp = new Date(new Date().getTime() + 450);
    while(waitTimestamp > new Date()){};

    spawn('/data/plugins/user_interface/audiotop/audiotop.py', {
    	detached: true
    });
}




// Configuration Methods -----------------------------------------------------------------------------

// Load the settings and display them in the "settings"-page
audiotop.prototype.getUIConfig = function() {
    var defer = libQ.defer();
	var self = this;

	var lang_code = this.commandRouter.sharedVars.get('language_code');

	self.commandRouter.i18nJson(__dirname+'/i18n/strings_'+lang_code+'.json',
		__dirname+'/i18n/strings_en.json',
		__dirname + '/UIConfig.json')
		.then(function(uiconf)
		{
			uiconf.sections[0].content[0].value = self.config.get('config_sleep_timer');
			uiconf.sections[0].content[1].value = self.config.get('config_metadata_url');

			defer.resolve(uiconf);
		})
		.fail(function()
		{
			// Something went wrong. Tell the user about it and abort loading the settings-page.
			self.commandRouter.pushToastMessage('error', "audiotop", "Error: Could not load settings");
			defer.reject(new Error());
		});

	return defer.promise;
};

// Function to save the settings the user wants to have
audiotop.prototype.saveUIConfig = function(data) {
   var defer = libQ.defer();
   var self = this;

   self.config.set('config_sleep_timer', data['sleep_timer']);
   self.config.set('config_metadata_url', data['metadata_url']);
   this.commandRouter.pushToastMessage('success', "audiotop", "Configuration saved sucessfully. Restarting plugin...");

   // After saving all settings, restart the audiotop
   var waitTimestamp = new Date(new Date().getTime() + 4000);
   while(waitTimestamp > new Date()){};
   restartAudiotop();

   // Tell Volumio everything went fine
   return defer.promise;
};

audiotop.prototype.setUIConfig = function(data) {
	var self = this;
	//Perform your installation tasks here
};

audiotop.prototype.getConf = function(varName) {
	var self = this;
	return ['config.json'];
};

audiotop.prototype.setConf = function(varName, varValue) {
	var self = this;
};
