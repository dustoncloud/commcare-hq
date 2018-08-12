hqDefine("app_manager/js/menu", function() {
    var setPublishStatus = function (isOn) {
        var layout = hqImport("hqwebapp/js/layout");
        if (isOn) {
            layout.showPublishStatus();
        } else {
            layout.hidePublishStatus();
        }
    };

    var initPublishStatus = function () {
        var currentAppVersionUrl = hqImport('hqwebapp/js/initial_page_data').reverse('current_app_version');
        var _checkPublishStatus = function () {
            $.ajax({
                url: currentAppVersionUrl,
                success: function (data) {
                    setPublishStatus((!data.latestBuild && data.currentVersion > 1) || (data.latestBuild !== null && data.latestBuild < data.currentVersion));
                },
            });
        };
        _checkPublishStatus();
        // check publish status every 20 seconds
        setInterval(_checkPublishStatus, 20000);

        // sniff ajax calls to other urls that make app changes
        hqImport("app_manager/js/app_manager_utils").handleAjaxAppChange(function() {
            setPublishStatus(true);
        });
    };

    $(function() {
        initPublishStatus();
    });

    return {
        setPublishStatus: setPublishStatus,
    };
});
