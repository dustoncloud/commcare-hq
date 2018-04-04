/* global module, inject, chai, MapOrSectorController */
"use strict";

var pageData = hqImport('hqwebapp/js/initial_page_data');

describe('Map Or Sector View Directive', function () {

    var $location, controller;

    pageData.registerUrl('icds-ng-template', 'template');
    pageData.registerUrl('icds_locations', 'icds_locations');

    beforeEach(module('icdsApp', function ($provide) {
        $provide.constant("userLocationId", null);
    }));

    beforeEach(inject(function ($controller, _$location_, storageService, locationsService) {
        $location = _$location_;

        controller = $controller(MapOrSectorController, {
            $location: $location,
            storageService: storageService,
            locationsService: locationsService,
        });
        controller.data = {
            "mapData": {
                "tooltips_data": {
                    "Morena -R": {
                        "in_month": 0,
                        "all": 0,
                    },
                    "Porsa": {
                        "in_month": 0,
                        "all": 0,
                    },
                    "Morena-U": {
                        "in_month": 0,
                        "all": 0,
                    },
                    "Ambah": {
                        "in_month": 0,
                        "all": 25,
                    },
                },
            },
        };
    }));

    it('tests instantiate the controller properly', function () {
        chai.expect(controller).not.to.be.a('undefined');
    });

    it('tests chart options', function () {
        var chart = controller.chartOptions.chart;
        var caption = controller.chartOptions.caption;
        assert.notEqual(chart, null);
        assert.notEqual(caption, null);
        assert.equal(controller.chartOptions.chart.type, 'multiBarHorizontalChart');
        assert.deepEqual(controller.chartOptions.chart.margin, {
            bottom: 40,
            left: 350,
        });
        assert.equal(controller.chartOptions.chart.showControls, false);
        assert.equal(controller.chartOptions.chart.showLegend, false);
        assert.equal(controller.chartOptions.chart.showValues, true);
        assert.equal(controller.chartOptions.chart.xAxis.showMaxMin, false);
        assert.equal(controller.chartOptions.chart.yAxis.axisLabelDistance, 20);

        assert.equal(controller.chartOptions.caption.enable, true);
        assert.deepEqual(controller.chartOptions.caption.css, {
            'text-align': 'center',
            'margin': '0 auto',
            'width': '900px',
        });

        assert.equal(controller.chartOptions.title.enable, true);
        assert.deepEqual(controller.chartOptions.title.css, {
            'text-align': 'right',
            'color': 'black',
        });
    });
    it('tests horizontal chart tooltip content', function () {
        var d = {
            "data": [
                "Ambah",
                0,
            ],
            "index": 0,
            "color": "rgb(0, 111, 223)",
            "value": "Ambah",
            "series": [
                {
                    "key": "",
                    "value": 0,
                    "color": "rgb(0, 111, 223)"
                },
            ],
        };

        var expected = 'templatePopup';
        controller.templatePopup = function (d) {
            return 'templatePopup';
        };
        var result = controller.chartOptions.chart.tooltip.contentGenerator(d);
        assert.equal(expected, result);
    });
});