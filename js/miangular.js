var app = angular.module('myApp', ['ngRoute', 'tc.chartjs']);
app.controller('mainController', function($scope, $http) {
        $http.get("data/itemsSummary.json")
        .success(function (data) {$scope.items = data;});
        $http.get("data/champsSummary.json")
        .success(function (data) {$scope.champs = data;});
    $scope.diff = 0;
    $scope.orderByField = 'winrate.after';
    $scope.reverseSort = true;
    $scope.reverseSortChange = function(item) {
        if (item == $scope.orderByField)
            $scope.reverseSort = !$scope.reverseSort;
        else
            $scope.reverseSort = true;
    }
    $scope.populateGrid= function(obj, idx){
        obj._index = idx;
        return !(obj._index % 11 )
    }
    $scope.howMany = 10;
    
});
app.filter('dosDecimales', function ($filter) {
    return function (input) {
        if (isNaN(input)) return input;
        return Math.round(input * 100) / 100;
    };
});
app.filter('startsWith', function(){
	return function(champs, str){
 
		//Create vars
		var matching_champs = [];		
 
		//Check if input matches current postcode
		if(champs && str){		 	
		 	//Loop through each region
			for(var i = 0; i < champs.length; i++){
				if(champs[i].key.substr(0, str.length).toLowerCase() == str.toLowerCase()){
					matching_champs.push(champs[i]);
				}
			}
 
			//Return matching regions
			return matching_champs;
		}
		else{
			return champs;
		}		
	}
});
app.directive('toggle', function(){
  return {
    restrict: 'A',
    link: function(scope, element, attrs){
      if (attrs.toggle=="tooltip"){
        $(element).tooltip();
      }
      if (attrs.toggle=="popover"){
        $(element).popover();
      }
    }
  };
});
app.controller('itemController', function($scope, $http, $routeParams) {
	$scope.itemId = $routeParams.item;
    /*
    item INTEGER NOT NULL,
    winrate REAL NOT NULL,
    kills INTEGER NOT NULL,
    deaths INTEGER NOT NULL,
    assists INTEGER NOT NULL,
    kda REAL NOT NULL,
    dmgDealt INTEGER NOT NULL,
    dmgTaken INTEGER NOT NULL,
    minions INTEGER NOT NULL,
    jungle INTEGER NOT NULL,
    heal INTEGER NOT NULL,
    gold INTEGER NOT NULL,
    */
    $http.get("data/itemsSummary.json")
        .success(function (data) {
            $scope.items = data;
            var keepGoing = true;
            angular.forEach($scope.items, function(elitem){
                if(keepGoing) {
                    //console.log("elitem: "+elitem);
                    if (elitem.item == $scope.itemId) {
                        $scope.el_item = elitem;
                        keepGoing = false;
                    }
                }
            });
         //Chart
        var fillBefore = 'rgba(175, 101, 214, 0.92)';
        var strokeBefore = 'rgb(95, 0, 136)';
        var hFillBefore = 'rgba(218, 134, 255, 0.92)';
        var hStrokeBefore = 'rgb(248, 211, 255)';
        var fillAfter = 'rgb(132, 216, 155)';
        var strokeAfter = 'rgb(0, 62, 14)';
        var hFillAfter = 'rgb(179, 245, 197)';
        var hStrokeAfter = 'rgb(227, 255, 233)';
        var wrbefore = Math.round($scope.el_item.winrate.before * 10000)/100;
        var wrafter = Math.round($scope.el_item.winrate.after * 10000)/100;
        if (Math.abs(wrafter-wrbefore) < 0.86) {
            wrbefore *= 100;
            wrafter *= 100;
        }
        // Chart.js Data
        $scope.data1 = {
          labels: ['Win rate'],
          datasets: [
            {
              label: 'Before',
              fillColor: fillBefore,
              strokeColor: strokeBefore,
              highlightFill: hFillBefore,
              highlightStroke: hStrokeBefore,
              data: [wrbefore]
            },
            {
              label: 'After',
              fillColor: fillAfter,
              strokeColor: strokeAfter,
              highlightFill: hFillAfter,
              highlightStroke: hStrokeAfter,
              data: [wrafter]
            }
          ]
        };
        $scope.data1 = {
          labels: [''],
          datasets: [
            {
              fillColor: fillAfter,
              strokeColor: strokeAfter,
              highlightFill: hFillAfter,
              highlightStroke: hStrokeAfter,
              data: [wrbefore, wrafter]
            }
          ]
        };
        $scope.data2 = {
          labels: ['Dmg Dealt'],
          datasets: [
            {
              label: 'Before',
              fillColor: fillBefore,
              strokeColor: strokeBefore,
              highlightFill: hFillBefore,
              highlightStroke: hStrokeBefore,
              data: [$scope.el_item.dmgDealt.before]
            },
            {
              label: 'After',
              fillColor: fillAfter,
              strokeColor: strokeAfter,
              highlightFill: hFillAfter,
              highlightStroke: hStrokeAfter,
              data: [$scope.el_item.dmgDealt.after]
            }
          ]
        };
        $scope.data2 = {
          labels: [''],
          datasets: [
            {
              fillColor: fillBefore,
              strokeColor: strokeBefore,
              highlightFill: hFillBefore,
              highlightStroke: hStrokeBefore,
              data: [$scope.el_item.dmgDealt.before, $scope.el_item.dmgDealt.after]
            }
          ]
        };
        $scope.data3 = {
          labels: ['Dmg Taken'],
          datasets: [
            {
              label: 'Before',
              fillColor: fillBefore,
              strokeColor: strokeBefore,
              highlightFill: hFillBefore,
              highlightStroke: hStrokeBefore,
              data: [$scope.el_item.dmgTaken.before]
            },
            {
              label: 'After',
              fillColor: fillAfter,
              strokeColor: strokeAfter,
              highlightFill: hFillAfter,
              highlightStroke: hStrokeAfter,
              data: [$scope.el_item.dmgTaken.after]
            }
          ]
        };
        $scope.data3 = {
          labels: [''],
          datasets: [
            {
              fillColor: fillAfter,
              strokeColor: strokeAfter,
              highlightFill: hFillAfter,
              highlightStroke: hStrokeAfter,
              data: [$scope.el_item.dmgTaken.before, $scope.el_item.dmgTaken.after]
            }
          ]
        };
        $scope.data4 = {
          labels: ['Gold'],
          datasets: [
            {
              label: 'Before',
              fillColor: fillBefore,
              strokeColor: strokeBefore,
              highlightFill: hFillBefore,
              highlightStroke: hStrokeBefore,
              data: [$scope.el_item.gold.before]
            },
            {
              label: 'After',
              fillColor: fillAfter,
              strokeColor: strokeAfter,
              highlightFill: hFillAfter,
              highlightStroke: hStrokeAfter,
              data: [$scope.el_item.gold.after]
            }
          ]
        };
        $scope.data4 = {
          labels: [''],
          datasets: [
            {
              fillColor: fillBefore,
              strokeColor: strokeBefore,
              highlightFill: hFillBefore,
              highlightStroke: hStrokeBefore,
              data: [$scope.el_item.gold.before, $scope.el_item.gold.after]
            }
          ]
        };


        $scope.data5 = {
          labels: ['Kills', 'Deaths', 'Assists', 'KDA'],
          datasets: [
            {
              label: 'Before',
              fillColor: fillBefore,
              strokeColor: strokeBefore,
              highlightFill: hFillBefore,
              highlightStroke: hStrokeBefore,
              data: [$scope.el_item.kills.before, $scope.el_item.deaths.before, $scope.el_item.assists.before, $scope.el_item.kda.before]
            },
            {
              label: 'After',
              fillColor: fillAfter,
              strokeColor: strokeAfter,
              highlightFill: hFillAfter,
              highlightStroke: hStrokeAfter,
              data: [$scope.el_item.kills.after, $scope.el_item.deaths.after, $scope.el_item.assists.after, $scope.el_item.kda.after]
            }
          ]
        };
        });
    $scope.diff = 0;
    $scope.orderByField = 'winrate.after';
    $scope.reverseSort = true;
    $scope.reverseSortChange = function(item) {
        if (item == $scope.orderByField)
            $scope.reverseSort = !$scope.reverseSort;
        else
            $scope.reverseSort = true;
    }
    
    // Chart.js Options
    $scope.options =  {
        //String - Scale label font colour	
      scaleFontColor : "#ddd",
      // Sets the chart to be responsive
      responsive: true,
      //Boolean - Whether the scale should start at zero, or an order of magnitude down from the lowest value
      scaleBeginAtZero : true,
      //Boolean - Whether grid lines are shown across the chart
      scaleShowGridLines : false,
      //String - Colour of the grid lines
      scaleGridLineColor : "rgba(0,0,0,.2)",
      //Number - Width of the grid lines
      scaleGridLineWidth : 1,
      //Boolean - If there is a stroke on each bar
      barShowStroke : true,
      //Number - Pixel width of the bar stroke
      barStrokeWidth : 2,
      //Number - Spacing between each of the X value sets
      barValueSpacing : 5,
      //Number - Spacing between data sets within X values
      barDatasetSpacing : 1,
      //String - A legend template
      legendTemplate : '<ul class="tc-chart-js-legend"><% for (var i=0; i<datasets.length; i++){%><li><span style="background-color:<%=datasets[i].fillColor%>"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>'
    };
    $scope.options2 = {
        //String - Scale label font colour	
      scaleFontColor : "#ddd",
      // Sets the chart to be responsive
      responsive: true,
      //Boolean - Whether the scale should start at zero, or an order of magnitude down from the lowest value
      scaleBeginAtZero : false,
      //Boolean - Whether grid lines are shown across the chart
      scaleShowGridLines : false,
      //String - Colour of the grid lines
      scaleGridLineColor : "rgb(0,0,0)",
      //Number - Width of the grid lines
      scaleGridLineWidth : 0,
      //Boolean - If there is a stroke on each bar
      barShowStroke : true,
      //Number - Pixel width of the bar stroke
      barStrokeWidth : 2,
      //Number - Spacing between each of the X value sets
      barValueSpacing : 5,
      //Number - Spacing between data sets within X values
      barDatasetSpacing : 1,
      //String - A legend template
      legendTemplate : '<ul class="tc-chart-js-legend"><% for (var i=0; i<datasets.length; i++){%><li><span style="background-color:<%=datasets[i].fillColor%>"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>'
    };    
});

app.controller('championController', function($scope, $http, $routeParams) {
	$scope.champKey = $routeParams.champion;

    $http.get("data/champsSummary.json")
        .success(function (data) {
            $scope.champs = data;
            var keepGoing = true;
            angular.forEach($scope.champs, function(elitem){
                if(keepGoing) {
                    //console.log("elitem: "+elitem);
                    if (elitem.key == $scope.champKey) {
                        $scope.champion = elitem;
                        keepGoing = false;
                    }
                }
            });
        
            var fillBefore = 'rgba(175, 101, 214, 0.92)';
            var strokeBefore = 'rgb(95, 0, 136)';
            var hFillBefore = 'rgba(218, 134, 255, 0.92)';
            var hStrokeBefore = 'rgb(248, 211, 255)';
            var fillAfter = 'rgb(132, 216, 155)';
            var strokeAfter = 'rgb(0, 62, 14)';
            var hFillAfter = 'rgb(179, 245, 197)';
            var hStrokeAfter = 'rgb(227, 255, 233)';
            $scope.data1 = {
                  labels: [],
                  datasets: [
                    {
                      label: 'Win Rate Before',
                      fillColor: fillBefore,
                      strokeColor: strokeBefore,
                      highlightFill: hFillBefore,
                      highlightStroke: hStrokeBefore,
                      data: []
                    },
                    {
                      label: 'Win Rate After',
                      fillColor: fillAfter,
                      strokeColor: strokeAfter,
                      highlightFill: hFillAfter,
                      highlightStroke: hStrokeAfter,
                      data: []
                    }
                    ]
                  };
            angular.forEach($scope.champion.items, function(elitem) {
                $scope.data1.labels.push(elitem.name);
                $scope.data1.datasets[0].data.push(Math.round(elitem.winrate.before*10000)/100);
                $scope.data1.datasets[1].data.push(Math.round(elitem.winrate.after*10000)/100);
            });
    });
        
    $scope.diff = 0;
    $scope.orderByField = 'winrate.after';
    $scope.reverseSort = true;
    $scope.reverseSortChange = function(item) {
        if (item == $scope.orderByField)
            $scope.reverseSort = !$scope.reverseSort;
        else
            $scope.reverseSort = true;
    }
    // Chart.js Options
    $scope.options =  {
      //String - Scale label font colour	
      scaleFontColor : "#ddd",	
      // Sets the chart to be responsive
      responsive: true,
      //Boolean - Whether the scale should start at zero, or an order of magnitude down from the lowest value
      scaleBeginAtZero : true,
      //Boolean - Whether grid lines are shown across the chart
      scaleShowGridLines : false,
      //String - Colour of the grid lines
      scaleGridLineColor : "rgba(0,0,0,.2)",
      //Number - Width of the grid lines
      scaleGridLineWidth : 1,
      //Boolean - If there is a stroke on each bar
      barShowStroke : true,
      //Number - Pixel width of the bar stroke
      barStrokeWidth : 2,
      //Number - Spacing between each of the X value sets
      barValueSpacing : 5,
      //Number - Spacing between data sets within X values
      barDatasetSpacing : 1,
      //String - A legend template
      legendTemplate : '<ul class="tc-chart-js-legend"><% for (var i=0; i<datasets.length; i++){%><li><span style="background-color:<%=datasets[i].fillColor%>"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>'
    };
    $scope.options2 = {
      //String - Scale label font colour	
      scaleFontColor : "#ddd",
      // Sets the chart to be responsive
      responsive: true,
      //Boolean - Whether the scale should start at zero, or an order of magnitude down from the lowest value
      scaleBeginAtZero : false,
      //Boolean - Whether grid lines are shown across the chart
      scaleShowGridLines : false,
      //String - Colour of the grid lines
      scaleGridLineColor : "rgb(0,0,0)",
      //Number - Width of the grid lines
      scaleGridLineWidth : 0,
      //Boolean - If there is a stroke on each bar
      barShowStroke : true,
      //Number - Pixel width of the bar stroke
      barStrokeWidth : 2,
      //Number - Spacing between each of the X value sets
      barValueSpacing : 5,
      //Number - Spacing between data sets within X values
      barDatasetSpacing : 1,
      //String - A legend template
      legendTemplate : '<ul class="tc-chart-js-legend"><% for (var i=0; i<datasets.length; i++){%><li><span style="background-color:<%=datasets[i].fillColor%>"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>'
    };    
});
// configure our routes
app.config(function($routeProvider) {
    $routeProvider

        // route for the home page
        .when('/', {
            templateUrl : '/AP-Rework-Comparator/partials/items_summary.html',
            controller  : 'mainController'
        })

        .when('/champions', {
            templateUrl : '/AP-Rework-Comparator/partials/champions.html',
            controller  : 'mainController'
        })
        
        // route for the about page
        .when('/item/:item', {
            templateUrl : '/AP-Rework-Comparator/partials/item.html',
            controller  : 'itemController'
        })

        // route for the contact page
        .when('/champion/:champion', {
            templateUrl : '/AP-Rework-Comparator/partials/champion.html',
            controller  : 'championController'
        })
        .otherwise({
            redirectTo: '/AP-Rework-Comparator'
        });
});
app.run(function ($rootScope, $anchorScroll) {
    $rootScope.$on('$routeChangeSuccess', function () {
        // Scroll to top on change
        $anchorScroll();
    });
});