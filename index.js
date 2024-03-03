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


module.exports = lcdcontroller;
function lcdcontroller(context) {
	var self = this;

	this.context = context;
	this.commandRouter = this.context.coreCommand;
	this.logger = this.context.logger;
	this.configManager = this.context.configManager;

}

// Tell Volumio that the settings are saved in a file called config.json
lcdcontroller.prototype.getConfigurationFiles = function()
{
	return ['config.json'];
}

lcdcontroller.prototype.onVolumioStart = function()
{
	var self = this;
	var configFile=this.commandRouter.pluginManager.getConfigurationFile(this.context,'config.json');
	this.config = new (require('v-conf'))();
	this.config.loadFile(configFile);

    return libQ.resolve();
}

// Tell Volumio what to do when the plugin gets enabled
lcdcontroller.prototype.onStart = function() {
    var self = this;
    var defer=libQ.defer();

    spawn('/usr/bin/killall', ['lcdmain.py'], {
    		detached: true
    });
    // Wait some time for '/usr/bin/killall' to complete
    var waitTimestamp = new Date(new Date().getTime() + 2000);
    while(waitTimestamp > new Date()){};
 
    spawn('/data/plugins/user_interface/lcdcontroller/LCDcontroller/lcdmain.py', {
      detached: true
    });


    // spawn('/usr/bin/killall', ['peppymeter.py'], {
    // 		detached: true
    // });
    // // Wait some time for '/usr/bin/killall' to complete
    // waitTimestamp = new Date(new Date().getTime() + 2000);
    // while(waitTimestamp > new Date()){};
    // spawn('/home/volumio/PeppyMeter/peppymeter.py', {
    // 	detached: true
    // });

    //exec('/home/volumio/PeppyMeter/peppymeter.py',{shell:true} , (err, stdout, stderr) => {});




    //  Once the Plugin has successfull started resolve the promise
    defer.resolve();

    return defer.promise;
};

// Tell Volumio what to do when the plugin gets disabled
lcdcontroller.prototype.onStop = function() {
    var self = this;
    var defer=libQ.defer();
    // Use spawn with option 'detached: true' to run a command. 'detached: false' will crash Volumio instantly, because 'child process /usr/bin/killall' exited.
    spawn('/usr/bin/killall', ['lcdmain.py'], {
    		detached: true
    });

    // spawn('/usr/bin/killall', ['peppymeter.py'], {
    // 		detached: true
    // });


    // Once the Plugin has successfull stopped resolve the promise
    defer.resolve();

    return libQ.resolve();
};

lcdcontroller.prototype.onRestart = function() {
    var self = this;
    restartLCD();
    // Use this if you need it
};

//restartLCD();

function restartLCD() {

    // spawn('/usr/bin/killall', ['peppymeter.py'], {
    // 		detached: true
    // });
    // // Wait some time for '/usr/bin/killall' to complete
    // waitTimestamp = new Date(new Date().getTime() + 450);
    // while(waitTimestamp > new Date()){};
    // spawn('/home/volumio/PeppyMeter/peppymeter.py', {
    // 	detached: true
    // });

    spawn('/usr/bin/killall', ['lcdmain.py'], {
    	detached: true
    });
    // Wait some time for '/usr/bin/killall' to complete
    var waitTimestamp = new Date(new Date().getTime() + 450);
    while(waitTimestamp > new Date()){};

    spawn('/data/plugins/user_interface/lcdcontroller/LCDcontroller/lcdmain.py', {
    	detached: true
    });




    //exec('/home/volumio/PeppyMeter/peppymeter.py',{shell:true} ,(err, stdout, stderr) => {});
}




// Configuration Methods -----------------------------------------------------------------------------

// Load the settings and display them in the "settings"-page
lcdcontroller.prototype.getUIConfig = function() {
    var defer = libQ.defer();
	var self = this;

	var lang_code = this.commandRouter.sharedVars.get('language_code');

	self.commandRouter.i18nJson(__dirname+'/i18n/strings_'+lang_code+'.json',
		__dirname+'/i18n/strings_en.json',
		__dirname + '/UIConfig.json')
		.then(function(uiconf)
		{

			// Load config_welcome_message_bool into UIconfig
			uiconf.sections[0].content[0].value = self.config.get('config_welcome_message_bool');
			// // Load config_welcome_message_duration into UIconfig
			uiconf.sections[0].content[1].value = self.config.get('config_welcome_message_duration');
			// // Load config_welcome_message_string_one into UIconfig
			uiconf.sections[0].content[2].value = self.config.get('config_welcome_message_string');
			uiconf.sections[0].content[3].value = self.config.get('config_sleep_timer');

			uiconf.sections[0].content[4].value = self.config.get('config_lcd_address');

            uiconf.sections[1].content[0].value = self.config.get('config_dsd_direct_bool');
			// Tell Volumio everything went very well
			defer.resolve(uiconf);
		})
		.fail(function()
		{
			// Something went wrong. Tell the user about it and abort loading the settings-page.
			self.commandRouter.pushToastMessage('error', "LCDcontroller", "Error: Could not load settings");
			defer.reject(new Error());
		});

	return defer.promise;
};
lcdcontroller.prototype.saveDSDConfig = function(data){
    var defer = libQ.defer();
    var self = this;
    this.commandRouter.pushToastMessage('success', "LCDcontroller", "DSD Setting saving and restarting audio...");

    if(data['dsd_direct_bool']) {
        sync('cp', ['/etc/mpd.conf.direct','/etc/mpd.conf'])
        sync('cp', ['/etc/asound.conf.direct','/etc/asound.conf'])
    }else{
        sync('cp', ['/etc/mpd.conf.dop','/etc/mpd.conf'])
        sync('cp', ['/etc/asound.conf.dop','/etc/asound.conf'])
    }
    sync('/usr/bin/sudo',['/etc/init.d/alsa-utils','restart'])
    sync('/usr/bin/sudo',['systemctl','restart','mpd'])

    self.config.set('config_dsd_direct_bool', data['dsd_direct_bool']);
    this.commandRouter.pushToastMessage('success', "LCDcontroller", "DSD Setting saved sucessfully.");

};
// Function to save the settings the user wants to have
lcdcontroller.prototype.saveUIConfig = function(data) {
   var defer = libQ.defer();
   var self = this;

   self.config.set('config_welcome_message_bool', data['welcome_message_bool']);
   self.config.set('config_welcome_message_duration', data['welcome_message_duration']);
   self.config.set('config_welcome_message_string', data['welcome_message_string']);
   self.config.set('config_lcd_address', data['lcd_address']);
   self.config.set('config_sleep_timer', data['sleep_timer']);
   this.commandRouter.pushToastMessage('success', "LCDcontroller", "Configuration saved sucessfully. Restarting plugin...");

   // After saving all settings, restart the LCDcontroller
   var waitTimestamp = new Date(new Date().getTime() + 4000);
   while(waitTimestamp > new Date()){};
   restartLCD();

   // Tell Volumio everything went fine
   return defer.promise;
};

lcdcontroller.prototype.setUIConfig = function(data) {
	var self = this;
	//Perform your installation tasks here
};

lcdcontroller.prototype.getConf = function(varName) {
	var self = this;
	return ['config.json'];
};

lcdcontroller.prototype.setConf = function(varName, varValue) {
	var self = this;
};
