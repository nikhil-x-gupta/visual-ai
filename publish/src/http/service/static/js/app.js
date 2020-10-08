(function () {
    'use strict';

    var app = angular.module('VisualApp', []);
    app.controller('FormCtrl', ['$scope', '$http', function($scope, $http) {
        $scope.panel = {};
      
        $scope.apply = function() {
            var json = angular.toJson($scope.panel);
            // console.log("config json:" + json);

	    var config = {
		headers : { 'Content-Type': 'application/json', "Accept": "text/plain" }
	    };

	    $http.post('/update/config', json, config).then(function (response) {
		// console.log("response:" + response);
	    }, function(error) {
		console.log("error:" + error);
	    });
        };

        $scope.upload = function() {
	    var model = "model"; 

	    var config = {
		headers : { 'Content-Type': 'application/json', "Accept": "text/plain" }
	    };

	    $http.post('/update/upload', model, config).then(function (response) {
		// console.log("response:" + response);
	    }, function(error) {
		console.log("error:" + error);
	    });
        };
	
        $scope.reset = function() {
            $scope.panel.overlay = true;
	    // $scope.panel.face = true;
            // $scope.panel.blur = false;
            $scope.panel.kafka = false;
            $scope.panel.stream = true;
        };

        $scope.reset();

      }]);
}());


