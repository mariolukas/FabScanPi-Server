/*
*/


/*
*/


(function() {
  var m, mods;

  mods = ['common.services.envProvider', 'common.filters.currentStateFilter', 'common.filters.toLabelFilter', 'common.filters.toResolutionValue', 'fabscan.directives.FSWebglDirective', 'fabscan.directives.FSMJPEGStream', 'fabscan.directives.FSModalDialog', 'fabscan.services.FSMessageHandlerService', 'fabscan.services.FSEnumService', 'fabscan.services.FSWebsocketConnectionFactory', 'fabscan.services.FSScanService', 'common.filters.scanDataAvailableFilter', 'common.services.Configuration', 'common.services.toastrWrapperSvc', 'fabscan.controller.FSPreviewController', 'fabscan.controller.FSAppController', 'fabscan.controller.FSSettingsController', 'fabscan.controller.FSScanController', 'fabscan.controller.FSLoadingController', 'fabscan.controller.FSShareController', 'ngTouch', '720kb.tooltips', 'ngProgress', 'vr.directives.slider', 'slick'];

  /*
  */


  /*
  */


  /*
  */


  /*
  */


  m = angular.module('fabscan', mods);

  m.config([
    'common.services.envProvider', function(envProvider) {
      if (envProvider.appConfig != null) {
        return envProvider.appConfig();
      }
    }
  ]);

  m.run([
    'common.services.env', function(env) {
      if (env.appRun != null) {
        return env.appRun();
      }
    }
  ]);

  m.config([
    '$httpProvider', function($httpProvider) {
      return $httpProvider.defaults.useXDomain = true;
    }
  ]);

  angular.element(document).ready(function() {
    return angular.bootstrap(document, ['fabscan']);
  });

}).call(this);

(function() {
  var name;

  name = 'fabscan.directives.FSMJPEGStream';

  angular.module(name, []).directive("mjpeg", [
    '$log', function($log) {
      return {
        restrict: 'E',
        replace: true,
        template: '<span></span>',
        scope: {
          'url': '='
        },
        link: function(scope, element, attrs) {
          scope.$watch('url', (function(newVal, oldVal) {
            var doc, iframe, iframeHtml;

            if (newVal) {
              iframe = document.createElement('iframe');
              iframe.setAttribute('width', '100%');
              iframe.setAttribute('frameborder', '0');
              iframe.setAttribute('scrolling', 'no');
              element.replaceWith(iframe);
              iframeHtml = '<html><head><base target="_parent" /><style type="text/css">html, body { margin: 0; padding: 0; height: 100%; width: 100%; }</style><script> function resizeParent() { var ifs = window.top.document.getElementsByTagName("iframe"); for (var i = 0, len = ifs.length; i < len; i++) { var f = ifs[i]; var fDoc = f.contentDocument || f.contentWindow.document; if (fDoc === document) { f.height = 0; f.height = document.body.scrollHeight; } } }</script></head><body onresize="resizeParent()"><img src="' + newVal + '" style="width: 100%; height: auto" onload="resizeParent()" /></body></html>';
              doc = iframe.document;
              if (iframe.contentDocument) {
                doc = iframe.contentDocument;
              } else if (iframe.contentWindow) {
                doc = iframe.contentWindow.document;
              }
              doc.open();
              doc.writeln(iframeHtml);
              doc.close();
            } else {
              element.html('<span></span>');
            }
          }), true);
        }
      };
    }
  ]);

}).call(this);

(function() {
  var name;

  name = 'fabscan.directives.FSModalDialog';

  angular.module(name, []).directive("modalDialog", [
    '$log', function($log) {}, {
      restrict: 'E',
      scope: {
        show: '='
      },
      replace: true,
      transclude: true,
      link: function(scope, element, attrs) {
        scope.dialogStyle = {};
        if (attrs.width) {
          scope.dialogStyle.width = attrs.width;
        }
        if (attrs.height) {
          scope.dialogStyle.height = attrs.height;
        }
        scope.hideModal = function() {
          scope.show = false;
        };
      },
      template: "<div class='ng-modal' ng-show='show'>    <div class='ng-modal-overlay' ng-click='hideModal()'></div>    <div class='ng-modal-dialog' ng-style='dialogStyle'>      <div class='ng-modal-close' ng-click='hideModal()'>X</div>      <div class='ng-modal-dialog-content' ng-transclude></div>    </div>  </div>"
    }
  ]);

}).call(this);

(function() {
  var name;

  name = 'fabscan.directives.slick';

  angular.module(name, []).directive("slickSlider", [
    '$log', '$timeout', function($log, $timeout) {
      return {
        restrict: 'A',
        link: function(scope, element, attrs) {
          $timeout(function() {
            $(element).slick(scope.$eval(attrs.slickSlider));
          });
        }
      };
    }
  ]);

}).call(this);

(function() {
  var name;

  name = 'fabscan.directives.FSWebglDirective';

  angular.module(name, []).directive("fsWebgl", [
    '$log', '$rootScope', '$http', 'fabscan.services.FSEnumService', 'common.services.Configuration', function($log, $rootScope, $http, FSEnumService, Configuration) {
      var postLink;

      return {
        restrict: "A",
        link: postLink = function(scope, element, attrs) {
          var camera, cameraTarget, colors, contH, contW, controls, currentPointcloudAngle, current_point, materials, mouseX, mouseY, mousedown, pointcloud, positions, rad, renderer, scanLoaded, scene, windowHalfX, windowHalfY;

          camera = void 0;
          scene = void 0;
          current_point = 0;
          renderer = void 0;
          positions = void 0;
          colors = void 0;
          controls = void 0;
          pointcloud = void 0;
          cameraTarget = void 0;
          currentPointcloudAngle = 0;
          mousedown = false;
          scanLoaded = false;
          scanLoaded = false;
          rad = 0;
          scope.height = window.innerHeight;
          scope.width = window.innerWidth;
          scope.fillcontainer = true;
          scope.materialType = 'lambert';
          scope.setPointHandlerCallback(scope.addPoints);
          scope.setClearViewHandlerCallback(scope.clearView);
          scope.loadPLYHandlerCallback(scope.loadPLY);
          scope.getRendererCallback(renderer);
          mouseX = 0;
          mouseY = 0;
          contW = (scope.fillcontainer ? element[0].clientWidth : scope.width);
          contH = scope.height;
          windowHalfX = contW / 2;
          windowHalfY = contH / 2;
          materials = {};
          $rootScope.$on('clearcanvas', function() {
            $log.info("view cleared");
            return scope.clearView();
          });
          scope.$on(FSEnumService.events.ON_STATE_CHANGED, function(events, data) {
            if (data['state'] === FSEnumService.states.SCANNING) {
              return scope.clearView();
            }
          });
          scope.$on(FSEnumService.events.ON_INFO_MESSAGE, function(event, data) {
            if (data['message'] === 'SCAN_CANCELED') {
              scope.clearView();
            }
            if (data['message'] === 'SCAN_COMPLETE') {
              scope.createPreviewImage(data['scan_id']);
              scope.scanComplete = true;
              return scope.currentPointcloudAngle = 0;
            }
          });
          scope.addShadowedLight = function(x, y, z, color, intensity) {
            var d, directionalLight;

            directionalLight = new THREE.DirectionalLight(color, intensity);
            directionalLight.position.set(x, y, z);
            scene.add(directionalLight);
            directionalLight.castShadow = true;
            d = 1;
            directionalLight.shadowCameraLeft = -d;
            directionalLight.shadowCameraRight = d;
            directionalLight.shadowCameraTop = d;
            directionalLight.shadowCameraBottom = -d;
            directionalLight.shadowCameraNear = 1;
            directionalLight.shadowCameraFar = 4;
            directionalLight.shadowMapWidth = 1024;
            directionalLight.shadowMapHeight = 1024;
            directionalLight.shadowBias = -0.005;
            return directionalLight.shadowDarkness = 0.15;
          };
          scope.init = function() {
            var axes, cylinder, geometry, material, plane;

            current_point = 0;
            camera = new THREE.PerspectiveCamera(38, window.innerWidth / window.innerHeight, 1, 800);
            camera.position.set(27, 5, 0);
            cameraTarget = new THREE.Vector3(10, 5, 0);
            scene = new THREE.Scene();
            scene.fog = new THREE.Fog(0x72645b, 20, 60);
            plane = new THREE.Mesh(new THREE.PlaneBufferGeometry(140, 100), new THREE.MeshPhongMaterial({
              ambient: 0x999999,
              color: 0x999999,
              specular: 0x101010
            }));
            plane.rotation.x = -Math.PI / 2;
            plane.position.y = -0.5;
            scene.add(plane);
            plane.receiveShadow = true;
            scene.add(new THREE.AmbientLight(0x777777));
            scope.addShadowedLight(1, 1, 1, 0xffffff, 1.35);
            scope.addShadowedLight(0.5, 1, -1, 0xffaa00, 1);
            axes = new THREE.AxisHelper(10);
            geometry = new THREE.CylinderGeometry(7, 7, 0.2, 32);
            material = new THREE.MeshBasicMaterial({
              color: 0xDEDEDE
            });
            cylinder = new THREE.Mesh(geometry, material);
            scene.add(cylinder);
            renderer = new THREE.WebGLRenderer({
              preserveDrawingBuffer: true
            });
            renderer.setClearColor(scene.fog.color);
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.gammaInput = true;
            renderer.gammaOutput = true;
            renderer.shadowMapEnabled = true;
            renderer.shadowMapCullFace = THREE.CullFaceBack;
            element[0].appendChild(renderer.domElement);
            window.addEventListener("resize", scope.onWindowResize, false);
            window.addEventListener("DOMMouseScroll", scope.onMouseWheel, false);
            window.addEventListener("mousewheel", scope.onMouseWheel, false);
            document.addEventListener("keydown", scope.onKeyDown, false);
            element[0].addEventListener("mousemove", scope.onMouseMove, false);
            element[0].addEventListener("mousedown", scope.onMouseDown, false);
            element[0].addEventListener("mouseup", scope.onMouseUp, false);
          };
          scope.createPreviewImage = function(id) {
            var screenshot;

            screenshot = renderer.domElement.toDataURL('image/png');
            return $http.post(Configuration.installation.httpurl + "api/v1/scan/preview/add/" + id, {
              image: screenshot,
              id: id
            }).success(function(response) {
              $log.info(response);
            });
          };
          scope.onWindowResize = function() {
            scope.resizeCanvas();
          };
          scope.onMouseDown = function(evt) {
            return mousedown = true;
          };
          scope.onMouseUp = function(evt) {
            return mousedown = false;
          };
          scope.onStart = function(evt) {
            return mousedown = true;
          };
          scope.onStop = function(evt) {
            return mousedown = false;
          };
          scope.onDrag = function(evt) {
            return $log.info(evt);
          };
          scope.onMouseMove = function(evt) {
            var d;

            if (mousedown) {
              d = (evt.movementX > 0 ? 0.1 : -0.1);
              if (pointcloud && scope.scanLoaded) {
                pointcloud.rotation.z += d;
              }
              if (pointcloud && scope.scanComplete) {
                return pointcloud.rotation.y += d;
              }
            }
          };
          scope.onKeyDown = function(evt) {
            var material;

            if (evt.keyCode === 189 || evt.keyCode === 109) {
              pointSize -= 0.003;
            }
            if (evt.keyCode === 187 || evt.keyCode === 107) {
              pointSize += 0.003;
            }
            if (evt.keyCode === 49) {
              changeColor("x");
            }
            if (evt.keyCode === 50) {
              changeColor("y");
            }
            if (evt.keyCode === 51) {
              changeColor("z");
            }
            if (evt.keyCode === 52) {
              changeColor("rgb");
            }
            material = new THREE.ParticleBasicMaterial({
              size: pointSize,
              vertexColors: true
            });
            pointcloud = new THREE.ParticleSystem(geometry, material);
            scene = new THREE.Scene();
            scene.add(pointcloud);
            return scope.render();
          };
          scope.resizeCanvas = function() {
            contW = (scope.fillcontainer ? element[0].clientWidth : scope.width);
            contH = scope.height;
            windowHalfX = contW / 2;
            windowHalfY = contH / 2;
            camera.aspect = contW / contH;
            camera.updateProjectionMatrix();
            renderer.setSize(contW, contH);
          };
          scope.resizeObject = function() {};
          scope.changeMaterial = function() {};
          scope.Float32Concat = function(first, second) {
            var firstLength, result;

            firstLength = first.length;
            result = new Float32Array(firstLength + second.length);
            result.set(first);
            result.set(second, firstLength);
            return result;
          };
          scope.loadPLY = function(file) {
            var loader;

            scope.clearView();
            scope.scanComplete = false;
            loader = new THREE.PLYLoader();
            loader.useColor = true;
            loader.colorsNeedUpdate = true;
            loader.addEventListener('progress', function(item) {
              return scope.progressHandler(item);
            });
            pointcloud = new THREE.Object3D;
            return loader.load(file, function(geometry) {
              var material;

              $log.info(geometry);
              material = new THREE.PointCloudMaterial({
                size: 0.15,
                vertexColors: THREE.FaceColors
              });
              pointcloud = new THREE.PointCloud(geometry, material);
              pointcloud.position.set(0, -0.25, 0);
              pointcloud.rotation.set(-Math.PI / 2, 0, 0);
              pointcloud.scale.set(0.1, 0.1, 0.1);
              scene.add(pointcloud);
            });
          };
          scope.addPoints = function(points, progress, resolution) {
            var color, degree, geometry, i, material, new_colors, new_positions, _results;

            scope.scanComplete = false;
            if (points.length > 0) {
              if (pointcloud) {
                currentPointcloudAngle = pointcloud.rotation.y;
                scene.remove(pointcloud);
              } else {
                currentPointcloudAngle = 90 * (Math.PI / 180);
              }
              geometry = new THREE.BufferGeometry();
              geometry.dynamic = true;
              new_positions = new Float32Array(points.length * 3);
              new_colors = new Float32Array(points.length * 3);
              i = 0;
              while (i < points.length) {
                new_positions[3 * i] = parseFloat(points[i]['x']);
                new_positions[3 * i + 1] = parseFloat(points[i]['y'] - 0.5);
                new_positions[3 * i + 2] = parseFloat(points[i]['z']);
                color = new THREE.Color("rgb(" + points[i]['r'] + "," + points[i]['g'] + "," + points[i]['b'] + ")");
                new_colors[3 * i] = color.r;
                new_colors[3 * i + 1] = color.g;
                new_colors[3 * i + 2] = color.b;
                i++;
              }
              if (positions === void 0) {
                positions = new_positions;
                colors = new_colors;
              } else {
                positions = scope.Float32Concat(positions, new_positions);
                colors = scope.Float32Concat(colors, new_colors);
              }
              geometry.addAttribute('position', new THREE.BufferAttribute(positions, 3));
              geometry.addAttribute('color', new THREE.BufferAttribute(colors, 3));
              material = new THREE.PointCloudMaterial({
                size: 0.2,
                vertexColors: THREE.VertexColors
              });
              pointcloud = new THREE.PointCloud(geometry, material);
              degree = 360 / resolution;
              $log.info(degree);
              scope.rad = degree * (Math.PI / 180);
              scene.add(pointcloud);
            }
            _results = [];
            while (i < points.length) {
              _points[current_point] = points;
              i++;
              _results.push(current_point++);
            }
            return _results;
          };
          scope.clearView = function() {
            if (pointcloud) {
              positions = void 0;
              colors = void 0;
              return scene.remove(pointcloud);
            }
          };
          scope.animate = function() {
            requestAnimationFrame(scope.animate);
            scope.render();
          };
          scope.render = function() {
            camera.lookAt(cameraTarget);
            renderer.render(scene, camera);
          };
          scope.$watch("newPoints", function(newValue, oldValue) {
            if (newValue !== oldValue) {
              scope.addPoints(newValue);
            }
          });
          scope.$watch("fillcontainer + width + height", function() {
            scope.resizeCanvas();
          });
          scope.$watch("scale", function() {
            scope.resizeObject();
          });
          scope.$watch("materialType", function() {});
          scope.init();
          scope.animate();
        }
      };
    }
  ]);

}).call(this);

/*
Takes a string and makes it lowercase
Example of a 'common' filter that can be shared by all views
*/


(function() {
  var name;

  name = 'common.filters.currentStateFilter';

  angular.module(name, []).filter('currentState', [
    '$log', 'fabscan.services.FSScanService', function($log, FSScanService) {
      return function(state) {
        if (state === FSScanService.getScannerState()) {
          return true;
        } else {
          return false;
        }
      };
    }
  ]);

}).call(this);

/*
Takes a string and makes it lowercase
Example of a 'common' filter that can be shared by all views
*/


(function() {
  var name;

  name = 'common.filters.scanDataAvailableFilter';

  angular.module(name, []).filter('scanDataAvailable', [
    '$log', 'fabscan.services.FSScanService', function($log, FSScanService) {
      return function() {
        if (FSScanService.getScanId() !== null) {
          return true;
        } else {
          return false;
        }
      };
    }
  ]);

}).call(this);

(function() {
  var name;

  name = 'common.filters.toLabelFilter';

  angular.module(name, []).filter('toLabel', [
    '$log', function($log) {
      return function(str) {
        var date, label_parts, time;

        label_parts = str.split("-");
        date = label_parts[0];
        time = label_parts[1];
        date = date.slice(0, 4) + "-" + date.slice(4);
        date = date.slice(0, 7) + "-" + date.slice(7);
        time = time.slice(0, 2) + ":" + time.slice(2);
        time = time.slice(0, 5) + ":" + time.slice(5);
        return date + " " + time;
      };
    }
  ]);

}).call(this);

/*
Takes a string and makes it lowercase
Example of a 'common' filter that can be shared by all views
*/


(function() {
  var name;

  name = 'common.filters.toLowerFilter';

  angular.module(name, []).filter('toLower', [
    '$log', function($log) {
      return function(str) {
        return str.toLowerCase();
      };
    }
  ]);

}).call(this);

(function() {
  var name;

  name = 'common.filters.toResolutionValue';

  angular.module(name, []).filter('toResolutionValue', [
    '$log', function($log) {
      return function(str) {
        if (str === -1) {
          return "best about 120 seconds";
        }
        if (str === -4) {
          return "good about 60 seconds";
        }
        if (str === -8) {
          return "medium 30 seconds";
        }
        if (str === -12) {
          return "low about 20 seconds";
        }
        if (str === -16) {
          return "lowest about 10 seconds";
        }
      };
    }
  ]);

}).call(this);

(function() {
  var name;

  name = 'common.services.Configuration';

  angular.module(name, []).factory(name, [
    '$location', function($location) {
      var config, host, localDebug;

      localDebug = $location.host() === 'localhost';
      config = null;
      if (localDebug) {
        host = "fabscanpi.local";
        config = {
          installation: {
            host: host,
            websocketurl: 'ws://' + host + ':8010/',
            httpurl: 'http://' + host + ':8080/'
          }
        };
      } else {
        host = $location.host();
        config = {
          installation: {
            host: host,
            websocketurl: 'ws://' + $location.host() + ':8010/',
            httpurl: 'http://' + $location.host() + '/'
          }
        };
      }
      return config;
    }
  ]);

}).call(this);

(function() {
  var name;

  name = 'fabscan.services.FSEnumService';

  angular.module(name, []).factory(name, function() {
    var FSEnumService;

    FSEnumService = {};
    FSEnumService.events = {
      ON_NEW_PROGRESS: 'ON_NEW_PROGRESS',
      ON_STATE_CHANGED: 'ON_STATE_CHANGED',
      COMMAND: 'COMMAND',
      ON_CLIENT_INIT: 'ON_CLIENT_INIT',
      ON_INFO_MESSAGE: 'ON_INFO_MESSAGE',
      SCAN_LOADED: "SCAN_LOADED"
    };
    FSEnumService.states = {
      IDLE: 'IDLE',
      SCANNING: 'SCANNING',
      SETTINGS: 'SETTINGS'
    };
    FSEnumService.commands = {
      SCAN: 'SCAN',
      START: 'START',
      STOP: 'STOP',
      UPDATE_SETTINGS: 'UPDATE_SETTINGS'
    };
    return FSEnumService;
  });

}).call(this);

(function() {
  var name;

  name = 'fabscan.services.FSMessageHandlerService';

  angular.module(name, []).factory(name, [
    '$log', '$timeout', '$rootScope', '$http', 'fabscan.services.FSWebsocketConnectionFactory', 'common.services.Configuration', function($log, $timeout, $rootScope, $http, FSWebsocketConnectionFactory, Configuration) {
      var FSMessageHandlerService, socket;

      socket = null;
      FSMessageHandlerService = {};
      FSMessageHandlerService.connectToScanner = function(scope) {
        scope.isConnected = false;
        socket = FSWebsocketConnectionFactory.createWebsocketConnection(Configuration.installation.websocketurl);
        socket.isConnected = function() {
          return scope.isConnected;
        };
        socket.onopen = function(event) {
          scope.isConnected = true;
          return console.log('Websocket connected to ' + socket.url);
        };
        socket.onerror = function(event) {
          return console.error(event);
        };
        socket.onclose = function(event) {
          scope.isConnected = false;
          socket = null;
          $rootScope.$broadcast("CONNECTION", scope.isConnected);
          $timeout(function() {
            return FSMessageHandlerService.connectToScanner(scope);
          }, 2000);
          return console.log("Connection closed");
        };
        return socket.onmessage = function(event) {
          var message;

          message = jQuery.parseJSON(event.data);
          return $rootScope.$broadcast(message['type'], message['data']);
        };
      };
      FSMessageHandlerService.sendData = function(message) {
        return socket.send(JSON.stringify(message));
      };
      return FSMessageHandlerService;
    }
  ]);

}).call(this);

(function() {
  var name;

  name = 'fabscan.services.FSScanService';

  angular.module(name, []).factory(name, [
    '$log', '$rootScope', 'fabscan.services.FSEnumService', 'fabscan.services.FSMessageHandlerService', function($log, $rootScope, FSEnumService, FSMessageHandlerService) {
      var service;

      service = {};
      service.state = FSEnumService.states.IDLE;
      service.scanId = null;
      service.getScanId = function() {
        return service.scanId;
      };
      service.setScanId = function(id) {
        return service.scanId = id;
      };
      service.startScan = function(options) {
        var message;

        service.state = FSEnumService.states.SCANNING;
        service.setScanId(null);
        message = {};
        message = {
          event: FSEnumService.events.COMMAND,
          data: {
            command: FSEnumService.commands.START
          }
        };
        FSMessageHandlerService.sendData(message);
        return $rootScope.$broadcast(FSEnumService.commands.START);
      };
      service.updateSettings = function(settings) {
        var message;

        message = {};
        message = {
          event: FSEnumService.events.COMMAND,
          data: {
            command: FSEnumService.commands.UPDATE_SETTINGS,
            settings: settings
          }
        };
        return FSMessageHandlerService.sendData(message);
      };
      service.startSettings = function(settings) {
        var message;

        message = {};
        message = {
          event: FSEnumService.events.COMMAND,
          data: {
            command: FSEnumService.commands.SCAN
          }
        };
        return FSMessageHandlerService.sendData(message);
      };
      service.stopScan = function() {
        var message;

        service.setScanId(null);
        message = {};
        message = {
          event: FSEnumService.events.COMMAND,
          data: {
            command: FSEnumService.commands.STOP
          }
        };
        FSMessageHandlerService.sendData(message);
        return $rootScope.$broadcast(FSEnumService.commands.STOP);
      };
      service.exitScan = function() {
        var message;

        message = {};
        message = {
          event: FSEnumService.events.COMMAND,
          data: {
            command: FSEnumService.commands.STOP
          }
        };
        return FSMessageHandlerService.sendData(message);
      };
      service.getScannerState = function() {
        return service.state;
      };
      service.setScannerState = function(state) {
        return service.state = state;
      };
      service.getSettings = function() {
        var message;

        message = {};
        return message = {
          event: FSEnumService.events.COMMAND
        };
      };
      return service;
    }
  ]);

}).call(this);

(function() {
  var name;

  name = 'fabscan.services.FSWebsocketConnectionFactory';

  angular.module(name, []).factory(name, function() {
    var service;

    service = {};
    service.createWebsocketConnection = function(url) {
      return new WebSocket(url);
    };
    return service;
  });

}).call(this);

/*
Example of a service shared across views.
Wrapper around the data layer for the app.
*/


(function() {
  var DataSvc, name;

  name = 'common.services.dataSvc';

  DataSvc = (function() {
    function DataSvc($log, $http, env) {
      this.$log = $log;
      this.$http = $http;
      this.env = env;
    }

    DataSvc.prototype._get = function(relPath) {
      return this.$http.get("" + this.env.serverUrl + "/" + relPath);
    };

    DataSvc.prototype.getPeople = function() {
      return this._get('people');
    };

    DataSvc.prototype.getPerson = function(id) {
      return this._get("person/" + id);
    };

    return DataSvc;

  })();

  angular.module(name, []).factory(name, [
    '$log', '$http', 'common.services.env', function($log, $http, env) {
      return new DataSvc($log, $http, env);
    }
  ]);

}).call(this);

/*
DEV
*/


(function() {
  var Environment, EnvironmentProvider, mod, modName, providerName;

  providerName = 'common.services.env';

  modName = "" + providerName + "Provider";

  Environment = (function() {
    function Environment() {}

    Environment.prototype.env = 'DEV';

    Environment.prototype.apiUrl = 'http://planungstool-testing.ambihome.de/api';

    return Environment;

  })();

  EnvironmentProvider = (function() {
    function EnvironmentProvider() {}

    EnvironmentProvider.prototype.$get = function() {
      return new Environment();
    };

    return EnvironmentProvider;

  })();

  mod = angular.module(modName, []);

  mod.provider(providerName, new EnvironmentProvider());

}).call(this);

/*
Example of how to wrap a 3rd party library, allowing it to be injectable instead of using the global var
*/


(function() {
  var name;

  name = 'common.services.toastrWrapperSvc';

  angular.module(name, []).factory(name, function() {
    return window.toastr;
  });

}).call(this);

(function() {
  var name;

  name = 'fabscan.controller.FSAppController';

  angular.module(name, []).controller(name, [
    '$log', '$scope', '$http', '$rootScope', 'ngProgress', 'common.services.toastrWrapperSvc', 'fabscan.services.FSMessageHandlerService', 'fabscan.services.FSEnumService', 'fabscan.services.FSScanService', function($log, $scope, $http, $rootScope, ngProgress, toastr, FSMessageHandlerService, FSEnumService, FSScanService) {
      $scope.streamUrl = " ";
      $scope.settings = {};
      $scope.scanComplete = false;
      $scope.scanLoaded = false;
      $scope.remainingTime = [];
      $scope.scanDataIsAvailable = function() {
        if (FSScanService.getScanId() !== null) {
          return true;
        } else {
          return false;
        }
      };
      $scope.$on("CONNECTION", function(event, connected) {
        return $log.info("Connected");
      });
      $scope.$on(FSEnumService.events.ON_CLIENT_INIT, function(event, data) {
        var _settings;

        $log.info("State: " + data['state']);
        _settings = data['settings'];
        _settings.resolution *= -1;
        angular.copy(_settings, $scope.settings);
        FSScanService.setScannerState(data['state']);
        return $scope.$apply();
      });
      $scope.$on(FSEnumService.events.ON_STATE_CHANGED, function(event, data) {
        $log.info("NEW STATE: " + data['state']);
        FSScanService.setScannerState(data['state']);
        $log.info(data);
        if (data['state'] === FSEnumService.states.IDLE) {
          ngProgress.complete();
        }
        return $scope.$apply();
      });
      $scope.$on(FSEnumService.events.ON_INFO_MESSAGE, function(event, data) {
        toastr.info(data['message']);
        return $scope.$apply();
      });
      return FSMessageHandlerService.connectToScanner($scope);
    }
  ]);

}).call(this);

(function() {
  var name;

  name = "fabscan.controller.FSLoadingController";

  angular.module(name, []).controller(name, [
    '$log', '$scope', '$rootScope', 'fabscan.services.FSScanService', 'fabscan.services.FSEnumService', function($log, $scope, $rootScope, FSScanService, FSEnum) {
      return $scope.loadPointCloud = function(pointcloud, id) {
        $scope.toggleLoadDialog();
        FSScanService.setScanId(id);
        $scope.scanComplete = false;
        toastr.info("Loading Scan " + id);
        return $scope.loadPLY(pointcloud);
      };
    }
  ]);

}).call(this);

(function() {
  var name;

  name = "fabscan.controller.FSPreviewController";

  angular.module(name, []).controller(name, [
    '$log', '$scope', '$rootScope', '$http', 'ngProgress', 'common.services.Configuration', 'fabscan.services.FSEnumService', 'fabscan.services.FSScanService', function($log, $scope, $rootScope, $http, ngProgress, Configuration, FSEnum, FSScanService) {
      var median;

      $scope.canvasWidth = 400;
      $scope.canvasHeight = 500;
      $scope.dofillcontainer = true;
      $scope.scale = 1;
      $scope.materialType = 'lambert';
      $scope.addPoints = null;
      $scope.resolution = null;
      $scope.progress = null;
      $scope.newPoints = null;
      $scope.loadPLY = null;
      $scope.renderer = null;
      $scope.showTextureScan = false;
      $scope.startTime = null;
      $scope.sampledRemainingTime = 0;
      $scope.$on(FSEnum.events.ON_STATE_CHANGED, function(event, data) {
        if (data['state'] === FSEnum.states.IDLE) {
          return $scope.showTextureScan = false;
        }
      });
      $rootScope.$on('clearView', function() {
        return $scope.clearView();
      });
      $scope.$on(FSEnum.events.ON_INFO_MESSAGE, function(event, data) {
        if (data['message'] === 'SCANNING_TEXTURE') {
          $scope.streamUrl = Configuration.installation.httpurl + '/stream/texture.mjpeg';
          $scope.showTextureScan = true;
        }
        if (data['message'] === 'SCANNING_OBJECT') {
          $scope.showTextureScan = false;
          $scope.streamUrl = "";
        }
        if (data['message'] === 'SCAN_COMPLETE') {
          FSScanService.setScanId(data['scan_id']);
          $scope.scanComplete = true;
          $scope.remainingTime = [];
          $scope.startTime = null;
        }
        if (data['message'] === 'SCAN_CANCELED') {
          $scope.remainingTime = [];
          $scope.startTime = null;
          return $scope.progress = 0;
        }
      });
      $scope.$on(FSEnum.events.ON_NEW_PROGRESS, function(event, data) {
        var percentage, timeTaken, _time_values;

        if (FSScanService.state !== FSEnum.states.IDLE) {
          $scope.resolution = data['resolution'];
          $scope.progress = data['progress'];
          $log.info($scope.progress);
          percentage = $scope.progress / $scope.resolution * 100;
          if ($scope.progress === 1) {
            $scope.startTime = Date.now();
          } else {
            timeTaken = Date.now() - $scope.startTime;
            $scope.remainingTime.push(Math.floor(((timeTaken / $scope.progress) * ($scope.resolution - $scope.progress)) / 1000));
            if ($scope.remainingTime.length > 20) {
              _time_values = $scope.remainingTime.slice(Math.max($scope.remainingTime.length - 8, 1));
            } else {
              _time_values = $scope.remainingTime;
            }
            $scope.sampledRemainingTime = Math.floor(median(_time_values));
            $log.info(percentage.toFixed(2) + "% complete");
            ngProgress.set(percentage);
          }
          if (percentage >= 100) {
            _time_values = [];
          }
          return $scope.addPoints(data['points'], data['progress'], data['resolution']);
        }
      });
      $scope.progressHandler = function(item) {
        var percentage;

        if ($scope.progress === 0) {
          ngProgress.start();
          $scope.progress = item.total;
        }
        percentage = item.loaded / item.total * 100;
        ngProgress.set(percentage);
        if (item.loaded === item.total) {
          $scope.scanLoaded = true;
          $scope.progress = 0;
          ngProgress.complete();
          return $scope.$apply();
        }
      };
      median = function(values) {
        var half;

        values.sort(function(a, b) {
          return a - b;
        });
        half = Math.floor(values.length / 2);
        if (values.length % 2) {
          return values[half];
        } else {
          return (values[half - 1] + values[half]) / 2.0;
        }
      };
      $scope.loadPLYHandlerCallback = function(callback) {
        return $scope.loadPLY = callback;
      };
      $scope.setPointHandlerCallback = function(callback) {
        return $scope.addPoints = callback;
      };
      $scope.setClearViewHandlerCallback = function(callback) {
        return $scope.clearView = callback;
      };
      return $scope.getRendererCallback = function(renderer) {
        return $scope.renderer = renderer;
      };
    }
  ]);

}).call(this);

(function() {
  var name;

  name = "fabscan.controller.FSScanController";

  angular.module(name, []).controller(name, [
    '$log', '$scope', '$rootScope', 'ngProgress', '$http', 'common.services.Configuration', 'fabscan.services.FSEnumService', 'fabscan.services.FSScanService', 'fabscan.services.FSMessageHandlerService', function($log, $scope, $rootScope, ngProgress, $http, Configuration, FSEnumService, FSScanService, FSMessageHandlerService) {
      $scope.showSettings = false;
      $scope.scanListLoaded = false;
      $scope.loadDialog = false;
      $scope.shareDialog = false;
      $scope.createScreenShot = null;
      $scope.scans = [];
      $scope.startScan = function() {
        $scope.stopStream();
        $scope.showSettings = false;
        $scope.scanComplete = false;
        $scope.scanLoaded = false;
        return FSScanService.startScan();
      };
      $scope.stopScan = function() {
        $scope.scanComplete = false;
        $scope.scanLoaded = false;
        $scope.remainingTime = [];
        return FSScanService.stopScan();
      };
      $scope.toggleShareDialog = function() {
        if ($scope.shareDialog) {
          return $scope.shareDialog = false;
        } else {
          $scope.loadDialog = false;
          return $scope.shareDialog = true;
        }
      };
      $scope.toggleLoadDialog = function() {
        var promise;

        if (!$scope.loadDialog) {
          promise = $http.get(Configuration.installation.httpurl + 'api/v1/scans/');
          return promise.then(function(payload) {
            $scope.scans = payload.data.scans;
            $scope.scanListLoaded = true;
            $scope.loadDialog = true;
            return $scope.shareDialog = false;
          });
        } else {
          $scope.scanListLoaded = false;
          $scope.loadDialog = false;
          return $scope.shareDialog = false;
        }
      };
      $scope.exitScanSettings = function() {
        $scope.stopStream();
        $scope.showSettings = false;
        return FSScanService.exitScan();
      };
      $scope.newScan = function() {
        if ($scope.loadDialog) {
          $scope.toggleLoadDialog();
        }
        if ($scope.shareDialog) {
          $scope.toggleShareDialog();
        }
        $scope.showSettings = true;
        return FSScanService.startSettings();
      };
      $scope.stopStream = function() {
        return $scope.streamUrl = " ";
      };
      return $scope.manviewhandler = function() {
        if ($scope.showSettings) {
          $scope.exitScanSettings();
        }
        if ($scope.shareDialog) {
          $scope.toggleShareDialog();
        }
        if ($scope.loadDialog) {
          return $scope.toggleLoadDialog();
        }
      };
    }
  ]);

}).call(this);

(function() {
  var name;

  name = "fabscan.controller.FSSettingsController";

  angular.module(name, []).controller(name, [
    '$log', '$scope', '$timeout', '$swipe', 'common.services.Configuration', 'fabscan.services.FSEnumService', 'fabscan.services.FSMessageHandlerService', 'fabscan.services.FSScanService', function($log, $scope, $timeout, $swipe, Configuration, FSEnumService, FSMessageHandlerService, FSScanService) {
      var updateSettings;

      $scope.streamUrl = Configuration.installation.httpurl + 'stream/preview.mjpeg';
      $scope.previewMode = "Webcam";
      $scope.selectedTab = 'general';
      $scope.timeout = null;
      updateSettings = function() {
        var _settings;

        _settings = {};
        angular.copy($scope.settings, _settings);
        _settings.resolution *= -1;
        return FSScanService.updateSettings(_settings);
      };
      if ($scope.isConnected) {
        updateSettings();
      }
      $scope.selectTab = function(tab) {
        $scope.selectedTab = tab;
        $scope.$broadcast('refreshSlider');
        return updateSettings();
      };
      $scope.togglePreviewMode = function() {
        return $log.info("Do Nothing");
      };
      $scope.showThresholdPreview = function() {
        $scope.streamUrl = Configuration.installation.httpurl + 'stream/threshold.mjpeg';
        return $scope.previewMode = "Threshold";
      };
      $scope.showWebcamPreview = function() {
        $scope.streamUrl = Configuration.installation.httpurl + '+stream/preview.mjpeg';
        return $scope.previewMode = "Webcam";
      };
      $scope.setColor = function() {
        return updateSettings();
      };
      $scope.colorIsSelected = function() {
        if ($scope.settings.color === "True") {
          return true;
        } else {
          return false;
        }
      };
      $scope.$watch('settings.resolution', function(newVal, oldVal) {
        if (newVal !== oldVal) {
          updateSettings();
          $timeout.cancel($scope.timeout);
          $scope.showResolutionValue = true;
          return $scope.timeout = $timeout((function() {
            $scope.showResolutionValue = false;
          }), 600);
        }
      }, true);
      $scope.$watch('settings.threshold', function(newVal, oldVal) {
        if (newVal !== oldVal) {
          updateSettings();
          $timeout.cancel($scope.timeout);
          $scope.showThresholdValue = true;
          return $scope.timeout = $timeout((function() {
            $scope.showThresholdValue = false;
          }), 200);
        }
      }, true);
      $scope.$watch('settings.camera.contrast', function(newVal, oldVal) {
        if (newVal !== oldVal) {
          updateSettings();
          $timeout.cancel($scope.timeout);
          $scope.showContrastValue = true;
          return $scope.timeout = $timeout((function() {
            $scope.showContrastValue = false;
          }), 200);
        }
      }, true);
      $scope.$watch('settings.camera.brightness', function(newVal, oldVal) {
        if (newVal !== oldVal) {
          updateSettings();
          $timeout.cancel($scope.timeout);
          $scope.showBrightnessValue = true;
          return $scope.timeout = $timeout((function() {
            $scope.showBrightnessValue = false;
          }), 200);
        }
      }, true);
      $scope.$watch('settings.led.red', function(newVal, oldVal) {
        if (newVal !== oldVal) {
          updateSettings();
          $timeout.cancel($scope.timeout);
          $scope.showLedRedValue = true;
          return $scope.timeout = $timeout((function() {
            $scope.showLedRedValue = false;
          }), 200);
        }
      }, true);
      $scope.$watch('settings.led.green', function(newVal, oldVal) {
        if (newVal !== oldVal) {
          updateSettings();
          $timeout.cancel($scope.timeout);
          $scope.showLedGreenValue = true;
          return $scope.timeout = $timeout((function() {
            $scope.showLedGreenValue = false;
          }), 200);
        }
      }, true);
      return $scope.$watch('settings.led.blue', function(newVal, oldVal) {
        if (newVal !== oldVal) {
          updateSettings();
          $timeout.cancel($scope.timeout);
          $scope.showLedBlueValue = true;
          return $scope.timeout = $timeout((function() {
            $scope.showLedBlueValue = false;
          }), 200);
        }
      }, true);
    }
  ]);

}).call(this);

(function() {
  var name;

  name = "fabscan.controller.FSShareController";

  angular.module(name, []).controller(name, [
    '$log', '$scope', '$rootScope', '$http', 'common.services.toastrWrapperSvc', 'common.services.Configuration', 'fabscan.services.FSScanService', function($log, $scope, $rootScope, $http, toaster, Configuration, FSScanService) {
      var promise;

      $scope.stl = null;
      $scope.ply = null;
      $scope.settings = null;
      $scope.id = FSScanService.getScanId();
      $log.info($scope.shareDialog);
      promise = $http.get(Configuration.installation.httpurl + 'api/v1/scans/' + FSScanService.getScanId());
      promise.then(function(payload) {
        $log.info(payload);
        $scope.stl = payload.data.mesh;
        $scope.ply = payload.data.pointcloud;
        return $scope.settings = payload.data.settings;
      });
      return $scope.deleteScan = function() {
        $scope.toggleShareDialog();
        promise = $http.get(Configuration.installation.httpurl + 'api/v1/delete/' + FSScanService.getScanId());
        return promise.then(function(payload) {
          $log.info(payload.data);
          toaster.info('Scan ' + FSScanService.getScanId() + ' deleted');
          FSScanService.setScanId(null);
          return $rootScope.$broadcast('clearView');
        });
      };
    }
  ]);

}).call(this);

(function() {
  var name;

  name = "fabscan.controller.FSStartupController";

  angular.module(name, []).controller(name, ['$log', '$scope', '$rootScope', 'fabscan.services.FSEnumService', 'fabscan.services.FSScanService', 'fabscan.services.FSMessageHandlerService', function($log, $scope, $rootScope, FSEnumService, FSScanService, FSMessageHandlerService) {}]);

}).call(this);
