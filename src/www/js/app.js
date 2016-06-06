<<<<<<< HEAD
/*
*/


/*
*/


(function() {
  var m, mods;

  mods = ['common.services.envProvider', 'common.filters.currentStateFilter', 'common.filters.toLabelFilter', 'common.filters.toResolutionValue', 'fabscan.directives.FSWebglDirective', 'fabscan.directives.FSMJPEGStream', 'fabscan.directives.FSModalDialog', 'fabscan.services.FSMessageHandlerService', 'fabscan.services.FSEnumService', 'fabscan.services.FSWebsocketConnectionFactory', 'fabscan.services.FSScanService', 'fabscan.services.FSi18nService', 'common.filters.scanDataAvailableFilter', 'common.services.Configuration', 'common.services.toastrWrapperSvc', 'fabscan.controller.FSPreviewController', 'fabscan.controller.FSAppController', 'fabscan.controller.FSSettingsController', 'fabscan.controller.FSScanController', 'fabscan.controller.FSLoadingController', 'fabscan.controller.FSShareController', 'ngTouch', '720kb.tooltips', 'ngProgress', 'vr.directives.slider', 'slickCarousel'];

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

  angular.module(name, []).directive('mjpeg', [
    '$log', function($log) {
      return {
        restrict: 'E',
        replace: true,
        template: '<span></span>',
        scope: {
          'url': '=',
          'mode': '='
        },
        link: function(scope, element, attrs) {
          scope.createFrame = function(newVal) {
            var doc, iframe, iframeHtml;

            iframe = document.createElement('iframe');
            iframe.setAttribute('frameborder', '0');
            iframe.setAttribute('scrolling', 'no');
            iframe.setAttribute('style', "height:100%;  position:absolute;");
            if (element.childElementCount > 0) {
              element.childNodes[0].destroy();
              element.append(iframe);
            } else {
              element.append(iframe);
            }
            if (scope.mode === "texture") {
              iframe.setAttribute('width', '100%');
              iframeHtml = '<html><head><base target="_parent" /><style type="text/css">html, body { margin: 0; padding: 0; height: 320px; }</style><script> function resizeParent() { var ifs = window.top.document.getElementsByTagName("iframe"); for (var i = 0, len = ifs.length; i < len; i++) { var f = ifs[i]; var fDoc = f.contentDocument || f.contentWindow.document; if (fDoc === document) { f.height = 0; f.height = document.body.scrollHeight; } } }</script></head><body style="" onresize="resizeParent()"><img src="' + newVal + '" style="z-index:1000; opacity: 0.4; width: 60%; bottom:70px; left:20%;  position:absolute;" onload="resizeParent()" /></body></html>';
            }
            if (scope.mode === "preview") {
              iframe.setAttribute('height', '240px');
              iframeHtml = '<html><head><base target="_parent" /><style type="text/css">html, body { margin: 0; padding: 0; height: 240px; }</style><script> function resizeParent() { var ifs = window.top.document.getElementsByTagName("iframe"); for (var i = 0, len = ifs.length; i < len; i++) { var f = ifs[i]; var fDoc = f.contentDocument || f.contentWindow.document; if (fDoc === document) { f.width = 0; f.width = document.body.scrollWidth; } } }</script></head><body onresize="resizeParent()"><img src="' + newVal + '" style="z-index:1000; opacity: 1.0; height:240px; position:absolute;" onload="resizeParent()" /><div style="position:absolute;  text-align:center; background-color:black; width:180px;  height:240px; float:left; z-index:-1000;"><img style="margin-top:100px; margin-left:70px width:50px; height:50px;" src="icons/spinner.gif" /></div></body></html>';
            }
            doc = iframe.document;
            if (iframe.contentDocument) {
              doc = iframe.contentDocument;
            } else if (iframe.contentWindow) {
              doc = iframe.contentWindow.document;
            }
            doc.open();
            doc.writeln(iframeHtml);
            return doc.close();
          };
          scope.$watch('url', (function(newVal, oldVal) {
            return scope.createFrame(newVal);
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
          var camera, cameraTarget, colors, contH, contW, controls, currentPointcloudAngle, current_point, materials, mesh, mouseX, mouseY, mousedown, pointcloud, positions, rad, renderer, scanLoaded, scene, windowHalfX, windowHalfY;

          camera = void 0;
          scene = void 0;
          current_point = 0;
          renderer = void 0;
          positions = void 0;
          colors = void 0;
          controls = void 0;
          pointcloud = void 0;
          mesh = void 0;
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
          scope.objectGeometry = null;
          scope.setPointHandlerCallback(scope.addPoints);
          scope.setClearViewHandlerCallback(scope.clearView);
          scope.loadPLYHandlerCallback(scope.loadPLY);
          scope.loadSTLHandlerCallback(scope.loadSTL);
          scope.getRendererCallback(renderer);
          scope.setRenderTypeCallback(scope.renderObjectAsType);
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
            scope.addShadowedLight(1, 1, 1, 0xffffff, 0.35);
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
            return $http.post(Configuration.installation.httpurl + "api/v1/scans/" + id + "/previews", {
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
                pointcloud.rotation.y += d;
              }
              if (mesh) {
                return mesh.rotation.z += d;
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
            return directionalLight.shadowBias = -0.005;
          };
          scope.renderMesh = function() {
            var material;

            scope.clearView();
            scope.objectGeometry.computeFaceNormals();
            material = new THREE.MeshBasicMaterial({
              shininess: 200,
              wireframe: false,
              vertexColors: THREE.FaceColors
            });
            mesh = new THREE.Mesh(scope.objectGeometry, material);
            mesh.position.set(0, -0.25, 0);
            mesh.rotation.set(-Math.PI / 2, 0, 0);
            mesh.scale.set(0.1, 0.1, 0.1);
            return scene.add(mesh);
          };
          scope.renderPLY = function() {
            var material;

            pointcloud = new THREE.Object3D;
            material = new THREE.PointsMaterial({
              size: 0.15,
              vertexColors: THREE.FaceColors
            });
            pointcloud = new THREE.Points(scope.objectGeometry, material);
            pointcloud.position.set(0, -0.25, 0);
            pointcloud.rotation.set(-Math.PI / 2, 0, 0);
            pointcloud.scale.set(0.1, 0.1, 0.1);
            return scene.add(pointcloud);
          };
          scope.renderObjectAsType = function(type) {
            if (type === "MESH") {
              scope.clearView();
              scope.renderMesh();
            }
            if (type === "POINTCLOUD") {
              scope.clearView();
              return scope.renderPLY();
            }
          };
          scope.loadSTL = function(file) {
            var loader;

            scope.clearView();
            scope.scanComplete = false;
            loader = new THREE.STLLoader();
            loader.load(file, function(geometry) {
              return scene.add(new THREE.Mesh(geometry));
            });
            return $log.info("Not implemented yet");
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
            return loader.load(file, function(objectGeometry) {
              scope.objectGeometry = objectGeometry;
              if (file.indexOf("mesh") > -1) {
                scope.renderMesh();
              } else {
                scope.renderPLY();
              }
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
              material = new THREE.PointsMaterial({
                size: 0.2,
                vertexColors: THREE.VertexColors
              });
              pointcloud = new THREE.Points(geometry, material);
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
              scene.remove(pointcloud);
              return scene.remove(mesh);
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
    '$log', '$location', function($log, $location) {
      var config, devDebug, host, localDebug;

      localDebug = $location.host() === 'localhost';
      config = null;
      devDebug = true;
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
            httpurl: 'http://' + $location.host() + ':8080/'
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
      UPDATE_SETTINGS: 'UPDATE_SETTINGS',
      MESHING: 'MESHING'
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
      service.runMeshing = function(scan_id, filter, format) {
        var message;

        message = {};
        message = {
          event: FSEnumService.events.COMMAND,
          data: {
            command: FSEnumService.commands.MESHING,
            scan_id: scan_id,
            format: format,
            filter: filter
          }
        };
        return FSMessageHandlerService.sendData(message);
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

(function() {
  var name;

  name = 'fabscan.services.FSi18nService';

  angular.module(name, []).factory(name, [
    '$log', '$rootScope', 'fabscan.services.FSEnumService', function($log, $rootScope, FSEnumService) {
      var service;

      service = {};
      service.translateKey = function(key, value) {
        return window.i18n[key][value]();
      };
      return service;
    }
  ]);

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
    '$log', '$scope', '$http', '$rootScope', 'ngProgress', 'common.services.toastrWrapperSvc', 'fabscan.services.FSMessageHandlerService', 'fabscan.services.FSEnumService', 'fabscan.services.FSScanService', 'fabscan.services.FSi18nService', function($log, $scope, $http, $rootScope, ngProgress, toastr, FSMessageHandlerService, FSEnumService, FSScanService, FSi18nService) {
      $scope.streamUrl = " ";
      $scope.settings = {};
      $scope.scanComplete = false;
      $scope.scanLoaded = false;
      $scope.remainingTime = [];
      $scope.server_version = void 0;
      $scope.firmware_version = void 0;
      $scope.scanLoading = false;
      $scope.scanIsComplete = function() {
        return $scope.scanComplete;
      };
      $scope.setScanIsComplete = function(value) {
        return $scope.scanComplete = value;
      };
      $scope.setScanIsLoading = function(value) {
        return $scope.scanLoading = value;
      };
      $scope.scanIsLoading = function() {
        return $scope.scanLoading;
      };
      $scope.setScanLoaded = function(value) {
        return $scope.scanLoaded = value;
      };
      $scope.scanIsLoaded = function() {
        return $scope.scanLoaded;
      };
      $scope.scanDataIsAvailable = function() {
        if ($scope.scanLoaded) {
          $log.info("scan loaded");
        }
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
        document.title = "FabScanPi " + data['server_version'];
        $scope.server_version = data['server_version'];
        $scope.firmware_version = data['firmware_version'];
        _settings = data['settings'];
        _settings.resolution *= -1;
        angular.copy(_settings, $scope.settings);
        FSScanService.setScannerState(data['state']);
        $log.debug("WebSocket connection ready...");
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
        var message;

        message = FSi18nService.translateKey('main', data['message']);
        switch (data['level']) {
          case "info":
            toastr.info(message, {
              timeOut: 5000
            });
            break;
          case "warn":
            toastr.warning(message);
            break;
          case "error":
            toastr.error(message, {
              timeOut: 0
            });
            break;
          case "success":
            toastr.success(message);
            break;
          default:
            toastr.info(message);
        }
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
      $scope.loadPointCloud = function(pointcloud, id) {
        $scope.setScanIsLoading(true);
        $scope.setScanIsComplete(false);
        $scope.toggleLoadDialog();
        FSScanService.setScanId(id);
        $scope.setScanLoaded(false);
        toastr.info("Loading scanned Pointcloud " + id);
        return $scope.loadPLY(pointcloud);
      };
      return $scope.loadMesh = function(mesh, id) {};
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
      $scope.loadSTL = null;
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
          $scope.setScanIsComplete(true);
          $scope.showTextureScan = false;
          $scope.remainingTime = [];
          $scope.startTime = null;
          $scope.sampledRemainingTime = 0;
        }
        if (data['message'] === 'SCAN_CANCELED' || data['message'] === 'SCAN_STOPED') {
          $scope.remainingTime = [];
          $scope.showTextureScan = false;
          $scope.startTime = null;
          $scope.progress = 0;
          return $scope.sampledRemainingTime = 0;
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
            ngProgress.start();
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
            $scope.sampledRemainingTime = 0;
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
          $scope.progress = 0;
          ngProgress.complete();
          percentage = 0;
          $scope.setScanIsLoading(false);
          $scope.setScanLoaded(true);
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
      $scope.setRenderTypeCallback = function(callback) {
        return $scope.renderObjectAsType = callback;
      };
      $scope.loadPLYHandlerCallback = function(callback) {
        return $scope.loadPLY = callback;
      };
      $scope.loadSTLHandlerCallback = function(callback) {
        return $scope.loadSTL = callback;
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
      var filter_promise;

      $scope.showSettings = false;
      $scope.scanListLoaded = false;
      $scope.loadDialog = false;
      $scope.shareDialog = false;
      $scope.createScreenShot = null;
      $scope.scans = [];
      $scope.m_filters = [];
      filter_promise = $http.get(Configuration.installation.httpurl + 'api/v1/filters');
      filter_promise.then(function(payload) {
        $log.info(payload);
        return $scope.m_filters = payload.data.filters;
      });
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
        $scope.stopStream();
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
          promise = $http.get(Configuration.installation.httpurl + 'api/v1/scans');
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

      $scope.streamUrl = Configuration.installation.httpurl + 'stream/laser.mjpeg';
      $scope.previewMode = "laser";
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
        updateSettings();
        return $scope.showLaserPreview();
      };
      $scope.setCalibrationTab = function() {
        $scope.selectedTab = 'calibration';
        $scope.$broadcast('refreshSlider');
        updateSettings();
        return $scope.showCalibrationPreview();
      };
      $scope.togglePreviewMode = function() {
        $log.info("Do Nothing");
        if ($scope.previewMode === "laser") {
          return $scope.showCalibrationPreview();
        } else {
          return $scope.showLaserPreview();
        }
      };
      $scope.showCalibrationPreview = function() {
        $scope.streamUrl = Configuration.installation.httpurl + 'stream/calibration.mjpeg';
        return $scope.previewMode = "calibration";
      };
      $scope.showLaserPreview = function() {
        $scope.streamUrl = Configuration.installation.httpurl + 'stream/laser.mjpeg';
        return $scope.previewMode = "laser";
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
      $scope.$watch('settings.laser_positions', function(newVal, oldVal) {
        if (newVal !== oldVal) {
          updateSettings();
          $timeout.cancel($scope.timeout);
          $scope.showPositionValue = true;
          return $scope.timeout = $timeout((function() {
            $scope.showPositionValue = false;
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
      $scope.$watch('settings.camera.saturation', function(newVal, oldVal) {
        if (newVal !== oldVal) {
          updateSettings();
          $timeout.cancel($scope.timeout);
          $scope.showSaturationValue = true;
          return $scope.timeout = $timeout((function() {
            $scope.showSaturationValue = false;
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
      var getFileExtension;

      $scope.settings = null;
      $scope.id = FSScanService.getScanId();
      $scope.selectedTab = 'download';
      $scope.raw_scans = [];
      $scope.meshes = [];
      $scope.file_formats = ['ply', 'stl', 'obj'];
      $scope.selectedFilter = $scope.m_filters[0];
      $scope.selectedFormat = $scope.file_formats[0];
      $scope.getScans = function() {
        var scan_promise;

        scan_promise = $http.get(Configuration.installation.httpurl + 'api/v1/scans/' + FSScanService.getScanId());
        return scan_promise.then(function(payload) {
          $log.info(payload);
          $scope.raw_scans = payload.data.raw_scans;
          $scope.meshes = payload.data.meshes;
          return $scope.settings = payload.data.settings;
        });
      };
      $scope.getScans();
      $scope.slickFormatConfig = {
        enabled: true,
        autoplay: false,
        draggable: false,
        autoplaySpeed: 3000,
        slidesToShow: 1,
        method: {},
        event: {
          afterChange: function(event, slick, currentSlide, nextSlide) {
            return $scope.selectedFormat = $(slick.$slides.get(currentSlide)).data('value');
          }
        }
      };
      $scope.slickFilterConfig = {
        enabled: true,
        autoplay: false,
        draggable: false,
        autoplaySpeed: 3000,
        slidesToShow: 1,
        method: {},
        event: {
          afterChange: function(event, slick, currentSlide, nextSlide) {
            return $scope.selectedFilter = $(slick.$slides.get(currentSlide)).data('value');
          }
        }
      };
      $scope.appendFormatListener = function() {
        $('.f_format').on('afterChange', function(event, slick, currentSlide, nextSlide) {
          return $scope.selectedFormat = $(slick.$slides.get(currentSlide)).data('value');
        });
      };
      $scope.appendFilterListener = function() {
        $('.m_filter').on('afterChange', function(event, slick, currentSlide, nextSlide) {
          return $scope.selectedFilter = $(slick.$slides.get(currentSlide)).data('value');
        });
      };
      $scope.selectTab = function(tab) {
        return $scope.selectedTab = tab;
      };
      $scope.nextSubSelection = function() {
        $('.filter-container').slick('slickNext');
        return false;
      };
      $scope.previewsSubSelection = function() {
        $('.filter-container').slick('slickPrev');
        return false;
      };
      $scope.deleteFile = function(filename) {
        var promise;

        $scope.toggleShareDialog();
        promise = $http["delete"](Configuration.installation.httpurl + 'api/v1/scans/' + FSScanService.getScanId() + '/files/' + filename);
        return promise.then(function(payload) {
          $log.info(payload.data);
          $scope.getScans();
          if (payload.data.response === "SCAN_DELETED") {
            toaster.info('Scan "' + payload.data['scan_id'] + '" deleted');
            FSScanService.setScanId(null);
            $scope.setScanLoaded(false);
            $rootScope.$broadcast('clearView');
          }
          return {
            "else": toaster.info('File "' + filename + '" deleted')
          };
        });
      };
      $scope.deleteScan = function() {
        var promise;

        $scope.toggleShareDialog();
        promise = $http["delete"](Configuration.installation.httpurl + 'api/v1/delete/' + FSScanService.getScanId());
        return promise.then(function(payload) {
          $log.info(payload.data);
          toaster.info('Scan ' + FSScanService.getScanId() + ' deleted');
          FSScanService.setScanId(null);
          return $rootScope.$broadcast('clearView');
        });
      };
      $scope.loadPointCloud = function(pointcloud) {
        $scope.toggleShareDialog();
        $scope.scanComplete = false;
        toastr.info("Loading file...");
        return $scope.loadPLY(pointcloud);
      };
      $scope.loadSTLMesh = function(filename) {
        $scope.toggleShareDialog();
        $scope.scanComplete = false;
        toastr.info("Loading file...");
        return $scope.loadSTL(filename);
      };
      getFileExtension = function(filename) {
        return filename.split('.').pop();
      };
      $scope.loadMesh = function(mesh) {
        var extension;

        extension = getFileExtension(mesh);
        if (extension === 'stl') {
          $scope.loadSTLMesh(mesh);
        }
        if (extension === 'ply') {
          return $scope.loadPLY(mesh);
        }
      };
      return $scope.runMeshing = function() {
        $scope.toggleShareDialog();
        return FSScanService.runMeshing(FSScanService.getScanId(), $scope.selectedFilter, $scope.selectedFormat);
      };
    }
  ]);

}).call(this);

(function() {
  var name;

  name = "fabscan.controller.FSStartupController";

  angular.module(name, []).controller(name, ['$log', '$scope', '$rootScope', 'fabscan.services.FSEnumService', 'fabscan.services.FSScanService', 'fabscan.services.FSMessageHandlerService', function($log, $scope, $rootScope, FSEnumService, FSScanService, FSMessageHandlerService) {}]);

}).call(this);
=======
(function(){var e,t;t=["common.services.envProvider","common.filters.currentStateFilter","common.filters.toLabelFilter","common.filters.toResolutionValue","fabscan.directives.FSWebglDirective","fabscan.directives.FSMJPEGStream","fabscan.directives.FSModalDialog","fabscan.services.FSMessageHandlerService","fabscan.services.FSEnumService","fabscan.services.FSWebsocketConnectionFactory","fabscan.services.FSScanService","fabscan.services.FSi18nService","common.filters.scanDataAvailableFilter","common.services.Configuration","common.services.toastrWrapperSvc","fabscan.controller.FSPreviewController","fabscan.controller.FSAppController","fabscan.controller.FSSettingsController","fabscan.controller.FSScanController","fabscan.controller.FSLoadingController","fabscan.controller.FSShareController","ngTouch","720kb.tooltips","ngProgress","vr.directives.slider","slickCarousel"],e=angular.module("fabscan",t),e.config(["common.services.envProvider",function(e){return null!=e.appConfig?e.appConfig():void 0}]),e.run(["common.services.env",function(e){return null!=e.appRun?e.appRun():void 0}]),e.config(["$httpProvider",function(e){return e.defaults.useXDomain=!0}]),angular.element(document).ready(function(){return angular.bootstrap(document,["fabscan"])})}).call(this),function(){var e;e="fabscan.directives.FSMJPEGStream",angular.module(e,[]).directive("mjpeg",["$log",function(){return{restrict:"E",replace:!0,template:"<span></span>",scope:{url:"=",mode:"="},link:function(e,t){e.createFrame=function(n){var r,i,o;return i=document.createElement("iframe"),i.setAttribute("frameborder","0"),i.setAttribute("scrolling","no"),i.setAttribute("style","height:100%;  position:absolute;"),t.childElementCount>0?(t.childNodes[0].destroy(),t.append(i)):t.append(i),"texture"===e.mode&&(i.setAttribute("width","100%"),o='<html><head><base target="_parent" /><style type="text/css">html, body { margin: 0; padding: 0; height: 100%; width: 100%; }</style><script> function resizeParent() { var ifs = window.top.document.getElementsByTagName("iframe"); for (var i = 0, len = ifs.length; i < len; i++) { var f = ifs[i]; var fDoc = f.contentDocument || f.contentWindow.document; if (fDoc === document) { f.height = 0; f.height = document.body.scrollHeight; } } }</script></head><body style="" onresize="resizeParent()"><img src="'+n+'" style="z-index:1000; opacity: 0.4; width: 60%; bottom:70px; left:20%;  position:absolute;" onload="resizeParent()" /></body></html>'),"preview"===e.mode&&(i.setAttribute("width","320px"),i.setAttribute("height","240px"),o='<html><head><base target="_parent" /><style type="text/css">html, body { margin: 0; padding: 0; height: 320px; width: 240px; }</style><script> function resizeParent() { var ifs = window.top.document.getElementsByTagName("iframe"); for (var i = 0, len = ifs.length; i < len; i++) { var f = ifs[i]; var fDoc = f.contentDocument || f.contentWindow.document; if (fDoc === document) { f.height = 0; f.height = document.body.scrollHeight; } } }</script></head><body onresize="resizeParent()"><img src="'+n+'" style="z-index:1000; opacity: 1.0; width: 320px; height:240px; position:absolute;" onload="resizeParent()" /><div style="position:absolute;  text-align:center; width:320px; height:240px; float:left; z-index:-1000; left:0;"><img style="margin-top:100px; width:50px; height:50px;" src="icons/spinner.gif" /></div></body></html>'),r=i.document,i.contentDocument?r=i.contentDocument:i.contentWindow&&(r=i.contentWindow.document),r.open(),r.writeln(o),r.close()},e.$watch("url",function(t){return e.createFrame(t)},!0)}}}])}.call(this),function(){var e;e="fabscan.directives.FSModalDialog",angular.module(e,[]).directive("modalDialog",["$log",function(){},{restrict:"E",scope:{show:"="},replace:!0,transclude:!0,link:function(e,t,n){e.dialogStyle={},n.width&&(e.dialogStyle.width=n.width),n.height&&(e.dialogStyle.height=n.height),e.hideModal=function(){e.show=!1}},template:"<div class='ng-modal' ng-show='show'>    <div class='ng-modal-overlay' ng-click='hideModal()'></div>    <div class='ng-modal-dialog' ng-style='dialogStyle'>      <div class='ng-modal-close' ng-click='hideModal()'>X</div>      <div class='ng-modal-dialog-content' ng-transclude></div>    </div>  </div>"}])}.call(this),function(){var e;e="fabscan.directives.slick",angular.module(e,[]).directive("slickSlider",["$log","$timeout",function(e,t){return{restrict:"A",link:function(e,n,r){t(function(){$(n).slick(e.$eval(r.slickSlider))})}}}])}.call(this),function(){var e;e="fabscan.directives.FSWebglDirective",angular.module(e,[]).directive("fsWebgl",["$log","$rootScope","$http","fabscan.services.FSEnumService","common.services.Configuration",function(e,t,n,r,i){var o;return{restrict:"A",link:o=function(o,a){var s,l,c,u,h,d,p,f,m,E,g,v,y,T,R,x,b,H,w,S,M;s=void 0,w=void 0,f=0,b=void 0,R=void 0,c=void 0,d=void 0,T=void 0,E=void 0,l=void 0,p=0,y=!1,H=!1,H=!1,x=0,o.height=window.innerHeight,o.width=window.innerWidth,o.fillcontainer=!0,o.materialType="lambert",o.objectGeometry=null,o.setPointHandlerCallback(o.addPoints),o.setClearViewHandlerCallback(o.clearView),o.loadPLYHandlerCallback(o.loadPLY),o.getRendererCallback(b),o.setRenderTypeCallback(o.renderObjectAsType),g=0,v=0,h=o.fillcontainer?a[0].clientWidth:o.width,u=o.height,S=h/2,M=u/2,m={},t.$on("clearcanvas",function(){return e.info("view cleared"),o.clearView()}),o.$on(r.events.ON_STATE_CHANGED,function(e,t){return t.state===r.states.SCANNING?o.clearView():void 0}),o.$on(r.events.ON_INFO_MESSAGE,function(e,t){return"SCAN_CANCELED"===t.message&&o.clearView(),"SCAN_COMPLETE"===t.message?(o.createPreviewImage(t.scan_id),o.scanComplete=!0,o.currentPointcloudAngle=0):void 0}),o.init=function(){var e,t,n,r,i;f=0,s=new THREE.PerspectiveCamera(38,window.innerWidth/window.innerHeight,1,800),s.position.set(27,5,0),l=new THREE.Vector3(10,5,0),w=new THREE.Scene,w.fog=new THREE.Fog(7496795,20,60),i=new THREE.Mesh(new THREE.PlaneBufferGeometry(140,100),new THREE.MeshPhongMaterial({ambient:10066329,color:10066329,specular:1052688})),i.rotation.x=-Math.PI/2,i.position.y=-.5,w.add(i),i.receiveShadow=!0,w.add(new THREE.AmbientLight(7829367)),o.addShadowedLight(1,1,1,16777215,.35),o.addShadowedLight(.5,1,-1,16755200,1),e=new THREE.AxisHelper(10),n=new THREE.CylinderGeometry(7,7,.2,32),r=new THREE.MeshBasicMaterial({color:14606046}),t=new THREE.Mesh(n,r),w.add(t),b=new THREE.WebGLRenderer({preserveDrawingBuffer:!0}),b.setClearColor(w.fog.color),b.setSize(window.innerWidth,window.innerHeight),b.gammaInput=!0,b.gammaOutput=!0,b.shadowMapEnabled=!0,b.shadowMapCullFace=THREE.CullFaceBack,a[0].appendChild(b.domElement),window.addEventListener("resize",o.onWindowResize,!1),window.addEventListener("DOMMouseScroll",o.onMouseWheel,!1),window.addEventListener("mousewheel",o.onMouseWheel,!1),document.addEventListener("keydown",o.onKeyDown,!1),a[0].addEventListener("mousemove",o.onMouseMove,!1),a[0].addEventListener("mousedown",o.onMouseDown,!1),a[0].addEventListener("mouseup",o.onMouseUp,!1)},o.createPreviewImage=function(t){var r;return r=b.domElement.toDataURL("image/png"),n.post(i.installation.httpurl+"api/v1/scans/"+t+"/previews",{image:r,id:t}).success(function(t){e.info(t)})},o.onWindowResize=function(){o.resizeCanvas()},o.onMouseDown=function(){return y=!0},o.onMouseUp=function(){return y=!1},o.onStart=function(){return y=!0},o.onStop=function(){return y=!1},o.onDrag=function(t){return e.info(t)},o.onMouseMove=function(e){var t;return y&&(t=e.movementX>0?.1:-.1,T&&o.scanLoaded&&(T.rotation.z+=t),T&&o.scanComplete&&(T.rotation.y+=t),E)?E.rotation.z+=t:void 0},o.onKeyDown=function(e){var t;return(189===e.keyCode||109===e.keyCode)&&(pointSize-=.003),(187===e.keyCode||107===e.keyCode)&&(pointSize+=.003),49===e.keyCode&&changeColor("x"),50===e.keyCode&&changeColor("y"),51===e.keyCode&&changeColor("z"),52===e.keyCode&&changeColor("rgb"),t=new THREE.ParticleBasicMaterial({size:pointSize,vertexColors:!0}),T=new THREE.ParticleSystem(geometry,t),w=new THREE.Scene,w.add(T),o.render()},o.resizeCanvas=function(){h=o.fillcontainer?a[0].clientWidth:o.width,u=o.height,S=h/2,M=u/2,s.aspect=h/u,s.updateProjectionMatrix(),b.setSize(h,u)},o.resizeObject=function(){},o.changeMaterial=function(){},o.Float32Concat=function(e,t){var n,r;return n=e.length,r=new Float32Array(n+t.length),r.set(e),r.set(t,n),r},o.addShadowedLight=function(e,t,n,r,i){var o,a;return a=new THREE.DirectionalLight(r,i),a.position.set(e,t,n),w.add(a),a.castShadow=!0,o=1,a.shadowCameraLeft=-o,a.shadowCameraRight=o,a.shadowCameraTop=o,a.shadowCameraBottom=-o,a.shadowCameraNear=1,a.shadowCameraFar=4,a.shadowMapWidth=1024,a.shadowMapHeight=1024,a.shadowBias=-.005},o.renderMesh=function(){var e;return o.clearView(),o.objectGeometry.computeFaceNormals(),e=new THREE.MeshBasicMaterial({shininess:200,wireframe:!1,vertexColors:THREE.FaceColors}),E=new THREE.Mesh(o.objectGeometry,e),E.position.set(0,-.25,0),E.rotation.set(-Math.PI/2,0,0),E.scale.set(.1,.1,.1),w.add(E)},o.renderPLY=function(){var e;return T=new THREE.Object3D,e=new THREE.PointsMaterial({size:.15,vertexColors:THREE.FaceColors}),T=new THREE.Points(o.objectGeometry,e),T.position.set(0,-.25,0),T.rotation.set(-Math.PI/2,0,0),T.scale.set(.1,.1,.1),w.add(T)},o.renderObjectAsType=function(e){return"MESH"===e&&(o.clearView(),o.renderMesh()),"POINTCLOUD"===e?(o.clearView(),o.renderPLY()):void 0},o.loadPLY=function(e){var t;return o.clearView(),o.scanComplete=!1,t=new THREE.PLYLoader,t.useColor=!0,t.colorsNeedUpdate=!0,t.addEventListener("progress",function(e){return o.progressHandler(e)}),t.load(e,function(t){o.objectGeometry=t,e.indexOf("mesh")>-1?o.renderMesh():o.renderPLY()})},o.addPoints=function(t,n,r){var i,a,s,l,u,h,d,m;if(o.scanComplete=!1,t.length>0){for(T?(p=T.rotation.y,w.remove(T)):p=90*(Math.PI/180),s=new THREE.BufferGeometry,s.dynamic=!0,d=new Float32Array(3*t.length),h=new Float32Array(3*t.length),l=0;t.length>l;)d[3*l]=parseFloat(t[l].x),d[3*l+1]=parseFloat(t[l].y-.5),d[3*l+2]=parseFloat(t[l].z),i=new THREE.Color("rgb("+t[l].r+","+t[l].g+","+t[l].b+")"),h[3*l]=i.r,h[3*l+1]=i.g,h[3*l+2]=i.b,l++;void 0===R?(R=d,c=h):(R=o.Float32Concat(R,d),c=o.Float32Concat(c,h)),s.addAttribute("position",new THREE.BufferAttribute(R,3)),s.addAttribute("color",new THREE.BufferAttribute(c,3)),u=new THREE.PointsMaterial({size:.2,vertexColors:THREE.VertexColors}),T=new THREE.Points(s,u),a=360/r,e.info(a),o.rad=a*(Math.PI/180),w.add(T)}for(m=[];t.length>l;)_points[f]=t,l++,m.push(f++);return m},o.clearView=function(){return T?(R=void 0,c=void 0,w.remove(T),w.remove(E)):void 0},o.animate=function(){requestAnimationFrame(o.animate),o.render()},o.render=function(){s.lookAt(l),b.render(w,s)},o.$watch("newPoints",function(e,t){e!==t&&o.addPoints(e)}),o.$watch("fillcontainer + width + height",function(){o.resizeCanvas()}),o.$watch("scale",function(){o.resizeObject()}),o.$watch("materialType",function(){}),o.init(),o.animate()}}}])}.call(this),function(){var e;e="common.filters.currentStateFilter",angular.module(e,[]).filter("currentState",["$log","fabscan.services.FSScanService",function(e,t){return function(e){return e===t.getScannerState()?!0:!1}}])}.call(this),function(){var e;e="common.filters.scanDataAvailableFilter",angular.module(e,[]).filter("scanDataAvailable",["$log","fabscan.services.FSScanService",function(e,t){return function(){return null!==t.getScanId()?!0:!1}}])}.call(this),function(){var e;e="common.filters.toLabelFilter",angular.module(e,[]).filter("toLabel",["$log",function(){return function(e){var t,n,r;return n=e.split("-"),t=n[0],r=n[1],t=t.slice(0,4)+"-"+t.slice(4),t=t.slice(0,7)+"-"+t.slice(7),r=r.slice(0,2)+":"+r.slice(2),r=r.slice(0,5)+":"+r.slice(5),t+" "+r}}])}.call(this),function(){var e;e="common.filters.toLowerFilter",angular.module(e,[]).filter("toLower",["$log",function(){return function(e){return e.toLowerCase()}}])}.call(this),function(){var e;e="common.filters.toResolutionValue",angular.module(e,[]).filter("toResolutionValue",["$log",function(){return function(e){return-1===e?"best about 120 seconds":-4===e?"good about 60 seconds":-8===e?"medium 30 seconds":-12===e?"low about 20 seconds":-16===e?"lowest about 10 seconds":void 0}}])}.call(this),function(){var e;e="common.services.Configuration",angular.module(e,[]).factory(e,["$log","$location",function(e,t){var n,r,i,o;return o="localhost"===t.host(),n=null,r=!0,o?(i="fabscanpi.local",n={installation:{host:i,websocketurl:"ws://"+i+":8010/",httpurl:"http://"+i+":8080/"}}):(i=t.host(),n={installation:{host:i,websocketurl:"ws://"+t.host()+":8010/",httpurl:"http://"+t.host()+":8080/"}}),n}])}.call(this),function(){var e;e="fabscan.services.FSEnumService",angular.module(e,[]).factory(e,function(){var e;return e={},e.events={ON_NEW_PROGRESS:"ON_NEW_PROGRESS",ON_STATE_CHANGED:"ON_STATE_CHANGED",COMMAND:"COMMAND",ON_CLIENT_INIT:"ON_CLIENT_INIT",ON_INFO_MESSAGE:"ON_INFO_MESSAGE",SCAN_LOADED:"SCAN_LOADED"},e.states={IDLE:"IDLE",SCANNING:"SCANNING",SETTINGS:"SETTINGS"},e.commands={SCAN:"SCAN",START:"START",STOP:"STOP",UPDATE_SETTINGS:"UPDATE_SETTINGS",MESHING:"MESHING"},e})}.call(this),function(){var e;e="fabscan.services.FSMessageHandlerService",angular.module(e,[]).factory(e,["$log","$timeout","$rootScope","$http","fabscan.services.FSWebsocketConnectionFactory","common.services.Configuration",function(e,t,n,r,i,o){var a,s;return s=null,a={},a.connectToScanner=function(e){return e.isConnected=!1,s=i.createWebsocketConnection(o.installation.websocketurl),s.isConnected=function(){return e.isConnected},s.onopen=function(){return e.isConnected=!0,console.log("Websocket connected to "+s.url)},s.onerror=function(e){return console.error(e)},s.onclose=function(){return e.isConnected=!1,s=null,n.$broadcast("CONNECTION",e.isConnected),t(function(){return a.connectToScanner(e)},2e3),console.log("Connection closed")},s.onmessage=function(e){var t;return t=jQuery.parseJSON(e.data),n.$broadcast(t.type,t.data)}},a.sendData=function(e){return s.send(JSON.stringify(e))},a}])}.call(this),function(){var e;e="fabscan.services.FSScanService",angular.module(e,[]).factory(e,["$log","$rootScope","fabscan.services.FSEnumService","fabscan.services.FSMessageHandlerService",function(e,t,n,r){var i;return i={},i.state=n.states.IDLE,i.scanId=null,i.getScanId=function(){return i.scanId},i.setScanId=function(e){return i.scanId=e},i.startScan=function(){var e;return i.state=n.states.SCANNING,i.setScanId(null),e={},e={event:n.events.COMMAND,data:{command:n.commands.START}},r.sendData(e),t.$broadcast(n.commands.START)},i.updateSettings=function(e){var t;return t={},t={event:n.events.COMMAND,data:{command:n.commands.UPDATE_SETTINGS,settings:e}},r.sendData(t)},i.startSettings=function(){var e;return e={},e={event:n.events.COMMAND,data:{command:n.commands.SCAN}},r.sendData(e)},i.stopScan=function(){var e;return i.setScanId(null),e={},e={event:n.events.COMMAND,data:{command:n.commands.STOP}},r.sendData(e),t.$broadcast(n.commands.STOP)},i.runMeshing=function(e,t,i){var o;return o={},o={event:n.events.COMMAND,data:{command:n.commands.MESHING,scan_id:e,format:i,filter:t}},r.sendData(o)},i.exitScan=function(){var e;return e={},e={event:n.events.COMMAND,data:{command:n.commands.STOP}},r.sendData(e)},i.getScannerState=function(){return i.state},i.setScannerState=function(e){return i.state=e},i.getSettings=function(){var e;return e={},e={event:n.events.COMMAND}},i}])}.call(this),function(){var e;e="fabscan.services.FSWebsocketConnectionFactory",angular.module(e,[]).factory(e,function(){var e;return e={},e.createWebsocketConnection=function(e){return new WebSocket(e)},e})}.call(this),function(){var e;e="fabscan.services.FSi18nService",angular.module(e,[]).factory(e,["$log","$rootScope","fabscan.services.FSEnumService",function(){var e;return e={},e.translateKey=function(e,t){return window.i18n[e][t]()},e}])}.call(this),function(){var e,t;t="common.services.dataSvc",e=function(){function e(e,t,n){this.$log=e,this.$http=t,this.env=n}return e.prototype._get=function(e){return this.$http.get(""+this.env.serverUrl+"/"+e)},e.prototype.getPeople=function(){return this._get("people")},e.prototype.getPerson=function(e){return this._get("person/"+e)},e}(),angular.module(t,[]).factory(t,["$log","$http","common.services.env",function(t,n,r){return new e(t,n,r)}])}.call(this),function(){var e,t,n,r,i;i="common.services.env",r=""+i+"Provider",e=function(){function e(){}return e.prototype.env="DEV",e.prototype.apiUrl="http://planungstool-testing.ambihome.de/api",e}(),t=function(){function t(){}return t.prototype.$get=function(){return new e},t}(),n=angular.module(r,[]),n.provider(i,new t)}.call(this),function(){var e;e="common.services.toastrWrapperSvc",angular.module(e,[]).factory(e,function(){return window.toastr})}.call(this),function(){var e;e="fabscan.controller.FSAppController",angular.module(e,[]).controller(e,["$log","$scope","$http","$rootScope","ngProgress","common.services.toastrWrapperSvc","fabscan.services.FSMessageHandlerService","fabscan.services.FSEnumService","fabscan.services.FSScanService","fabscan.services.FSi18nService",function(e,t,n,r,i,o,a,s,l,c){return t.streamUrl=" ",t.settings={},t.scanComplete=!1,t.scanLoaded=!1,t.remainingTime=[],t.server_version=void 0,t.firmware_version=void 0,t.scanLoading=!1,t.scanIsComplete=function(){return t.scanComplete},t.setScanIsComplete=function(e){return t.scanComplete=e},t.setScanIsLoading=function(e){return t.scanLoading=e},t.scanIsLoading=function(){return t.scanLoading},t.setScanLoaded=function(e){return t.scanLoaded=e},t.scanIsLoaded=function(){return t.scanLoaded},t.scanDataIsAvailable=function(){return t.scanLoaded&&e.info("scan loaded"),null!==l.getScanId()?!0:!1},t.$on("CONNECTION",function(){return e.info("Connected")}),t.$on(s.events.ON_CLIENT_INIT,function(n,r){var i;return e.info("State: "+r.state),document.title="FabScanPi "+r.server_version,t.server_version=r.server_version,t.firmware_version=r.firmware_version,i=r.settings,i.resolution*=-1,angular.copy(i,t.settings),l.setScannerState(r.state),e.debug("WebSocket connection ready..."),t.$apply()}),t.$on(s.events.ON_STATE_CHANGED,function(n,r){return e.info("NEW STATE: "+r.state),l.setScannerState(r.state),e.info(r),r.state===s.states.IDLE&&i.complete(),t.$apply()}),t.$on(s.events.ON_INFO_MESSAGE,function(e,n){var r;switch(r=c.translateKey("main",n.message),n.level){case"info":o.info(r,{timeOut:5e3});break;case"warn":o.warning(r);break;case"error":o.error(r,{timeOut:0});break;case"success":o.success(r);break;default:o.info(r)}return t.$apply()}),a.connectToScanner(t)}])}.call(this),function(){var e;e="fabscan.controller.FSLoadingController",angular.module(e,[]).controller(e,["$log","$scope","$rootScope","fabscan.services.FSScanService","fabscan.services.FSEnumService",function(e,t,n,r){return t.loadPointCloud=function(e,n){return t.setScanIsLoading(!0),t.setScanIsComplete(!1),t.$apply(),t.toggleLoadDialog(),r.setScanId(n),t.setScanLoaded(!1),toastr.info("Loading scanned Pointcloud "+n),t.loadPLY(e)},t.loadMesh=function(){}}])}.call(this),function(){var e;e="fabscan.controller.FSPreviewController",angular.module(e,[]).controller(e,["$log","$scope","$rootScope","$http","ngProgress","common.services.Configuration","fabscan.services.FSEnumService","fabscan.services.FSScanService",function(e,t,n,r,i,o,a,s){var l;return t.canvasWidth=400,t.canvasHeight=500,t.dofillcontainer=!0,t.scale=1,t.materialType="lambert",t.addPoints=null,t.resolution=null,t.progress=null,t.newPoints=null,t.loadPLY=null,t.renderer=null,t.showTextureScan=!1,t.startTime=null,t.sampledRemainingTime=0,t.$on(a.events.ON_STATE_CHANGED,function(e,n){return n.state===a.states.IDLE?t.showTextureScan=!1:void 0}),n.$on("clearView",function(){return t.clearView()}),t.$on(a.events.ON_INFO_MESSAGE,function(e,n){return"SCANNING_TEXTURE"===n.message&&(t.streamUrl=o.installation.httpurl+"/stream/texture.mjpeg",t.showTextureScan=!0),"SCANNING_OBJECT"===n.message&&(t.showTextureScan=!1,t.streamUrl=""),"SCAN_COMPLETE"===n.message&&(s.setScanId(n.scan_id),t.setScanIsComplete(!0),t.showTextureScan=!1,t.remainingTime=[],t.startTime=null,t.sampledRemainingTime=0),"SCAN_CANCELED"===n.message||"SCAN_STOPED"===n.message?(t.remainingTime=[],t.showTextureScan=!1,t.startTime=null,t.progress=0,t.sampledRemainingTime=0):void 0}),t.$on(a.events.ON_NEW_PROGRESS,function(n,r){var o,c,u;return s.state!==a.states.IDLE?(t.resolution=r.resolution,t.progress=r.progress,e.info(t.progress),o=100*(t.progress/t.resolution),1===t.progress?(t.startTime=Date.now(),i.start()):(c=Date.now()-t.startTime,t.remainingTime.push(Math.floor(c/t.progress*(t.resolution-t.progress)/1e3)),u=t.remainingTime.length>20?t.remainingTime.slice(Math.max(t.remainingTime.length-8,1)):t.remainingTime,t.sampledRemainingTime=Math.floor(l(u)),e.info(o.toFixed(2)+"% complete"),i.set(o)),o>=100&&(t.sampledRemainingTime=0,u=[]),t.addPoints(r.points,r.progress,r.resolution)):void 0}),t.progressHandler=function(e){var n;return 0===t.progress&&(i.start(),t.progress=e.total),n=100*(e.loaded/e.total),i.set(n),e.loaded===e.total?(t.progress=0,i.complete(),n=0,t.setScanIsLoading(!1),t.setScanLoaded(!0),t.$apply()):void 0},l=function(e){var t;return e.sort(function(e,t){return e-t}),t=Math.floor(e.length/2),e.length%2?e[t]:(e[t-1]+e[t])/2},t.setRenderTypeCallback=function(e){return t.renderObjectAsType=e},t.loadPLYHandlerCallback=function(e){return t.loadPLY=e},t.setPointHandlerCallback=function(e){return t.addPoints=e},t.setClearViewHandlerCallback=function(e){return t.clearView=e},t.getRendererCallback=function(e){return t.renderer=e}}])}.call(this),function(){var e;e="fabscan.controller.FSScanController",angular.module(e,[]).controller(e,["$log","$scope","$rootScope","ngProgress","$http","common.services.Configuration","fabscan.services.FSEnumService","fabscan.services.FSScanService","fabscan.services.FSMessageHandlerService",function(e,t,n,r,i,o,a,s){var l;return t.showSettings=!1,t.scanListLoaded=!1,t.loadDialog=!1,t.shareDialog=!1,t.createScreenShot=null,t.scans=[],t.m_filters=[],l=i.get(o.installation.httpurl+"api/v1/filters"),l.then(function(n){return e.info(n),t.m_filters=n.data.filters}),t.startScan=function(){return t.stopStream(),t.showSettings=!1,t.scanComplete=!1,t.scanLoaded=!1,s.startScan()},t.stopScan=function(){return t.scanComplete=!1,t.scanLoaded=!1,t.remainingTime=[],t.stopStream(),s.stopScan()},t.toggleShareDialog=function(){return t.shareDialog?t.shareDialog=!1:(t.loadDialog=!1,t.shareDialog=!0)},t.toggleLoadDialog=function(){var e;return t.loadDialog?(t.scanListLoaded=!1,t.loadDialog=!1,t.shareDialog=!1):(e=i.get(o.installation.httpurl+"api/v1/scans"),e.then(function(e){return t.scans=e.data.scans,t.scanListLoaded=!0,t.loadDialog=!0,t.shareDialog=!1}))},t.exitScanSettings=function(){return t.stopStream(),t.showSettings=!1,s.exitScan()},t.newScan=function(){return t.loadDialog&&t.toggleLoadDialog(),t.shareDialog&&t.toggleShareDialog(),t.showSettings=!0,s.startSettings()},t.stopStream=function(){return t.streamUrl=" "},t.manviewhandler=function(){return t.showSettings&&t.exitScanSettings(),t.shareDialog&&t.toggleShareDialog(),t.loadDialog?t.toggleLoadDialog():void 0}}])}.call(this),function(){var e;e="fabscan.controller.FSSettingsController",angular.module(e,[]).controller(e,["$log","$scope","$timeout","$swipe","common.services.Configuration","fabscan.services.FSEnumService","fabscan.services.FSMessageHandlerService","fabscan.services.FSScanService",function(e,t,n,r,i,o,a,s){var l;return t.streamUrl=i.installation.httpurl+"stream/laser.mjpeg",t.previewMode="laser",t.selectedTab="general",t.timeout=null,l=function(){var e;return e={},angular.copy(t.settings,e),e.resolution*=-1,s.updateSettings(e)},t.isConnected&&l(),t.selectTab=function(e){return t.selectedTab=e,t.$broadcast("refreshSlider"),l(),t.showLaserPreview()},t.setCalibrationTab=function(){return t.selectedTab="calibration",t.$broadcast("refreshSlider"),l(),t.showCalibrationPreview()},t.togglePreviewMode=function(){return e.info("Do Nothing"),"laser"===t.previewMode?t.showCalibrationPreview():t.showLaserPreview()},t.showCalibrationPreview=function(){return t.streamUrl=i.installation.httpurl+"stream/calibration.mjpeg",t.previewMode="calibration"},t.showLaserPreview=function(){return t.streamUrl=i.installation.httpurl+"stream/laser.mjpeg",t.previewMode="laser"},t.setColor=function(){return l()},t.colorIsSelected=function(){return"True"===t.settings.color?!0:!1},t.$watch("settings.resolution",function(e,r){return e!==r?(l(),n.cancel(t.timeout),t.showResolutionValue=!0,t.timeout=n(function(){t.showResolutionValue=!1},600)):void 0},!0),t.$watch("settings.laser_positions",function(e,r){return e!==r?(l(),n.cancel(t.timeout),t.showPositionValue=!0,t.timeout=n(function(){t.showPositionValue=!1},600)):void 0},!0),t.$watch("settings.threshold",function(e,r){return e!==r?(l(),n.cancel(t.timeout),t.showThresholdValue=!0,t.timeout=n(function(){t.showThresholdValue=!1},200)):void 0},!0),t.$watch("settings.camera.saturation",function(e,r){return e!==r?(l(),n.cancel(t.timeout),t.showSaturationValue=!0,t.timeout=n(function(){t.showSaturationValue=!1},200)):void 0},!0),t.$watch("settings.camera.contrast",function(e,r){return e!==r?(l(),n.cancel(t.timeout),t.showContrastValue=!0,t.timeout=n(function(){t.showContrastValue=!1},200)):void 0},!0),t.$watch("settings.camera.brightness",function(e,r){return e!==r?(l(),n.cancel(t.timeout),t.showBrightnessValue=!0,t.timeout=n(function(){t.showBrightnessValue=!1},200)):void 0},!0),t.$watch("settings.led.red",function(e,r){return e!==r?(l(),n.cancel(t.timeout),t.showLedRedValue=!0,t.timeout=n(function(){t.showLedRedValue=!1},200)):void 0},!0),t.$watch("settings.led.green",function(e,r){return e!==r?(l(),n.cancel(t.timeout),t.showLedGreenValue=!0,t.timeout=n(function(){t.showLedGreenValue=!1},200)):void 0},!0),t.$watch("settings.led.blue",function(e,r){return e!==r?(l(),n.cancel(t.timeout),t.showLedBlueValue=!0,t.timeout=n(function(){t.showLedBlueValue=!1},200)):void 0},!0)}])}.call(this),function(){var e;e="fabscan.controller.FSShareController",angular.module(e,[]).controller(e,["$log","$scope","$rootScope","$http","common.services.toastrWrapperSvc","common.services.Configuration","fabscan.services.FSScanService",function(e,t,n,r,i,o,a){return t.settings=null,t.id=a.getScanId(),t.selectedTab="download",t.raw_scans=[],t.meshes=[],t.file_formats=["ply","stl","obj"],t.selectedFilter=t.m_filters[0],t.selectedFormat=t.file_formats[0],t.getScans=function(){var n;return n=r.get(o.installation.httpurl+"api/v1/scans/"+a.getScanId()),n.then(function(n){return e.info(n),t.raw_scans=n.data.raw_scans,t.meshes=n.data.meshes,t.settings=n.data.settings})},t.getScans(),t.slickFormatConfig={enabled:!0,autoplay:!1,draggable:!1,autoplaySpeed:3e3,slidesToShow:1,method:{},event:{afterChange:function(e,n,r){return t.selectedFormat=$(n.$slides.get(r)).data("value")}}},t.slickFilterConfig={enabled:!0,autoplay:!1,draggable:!1,autoplaySpeed:3e3,slidesToShow:1,method:{},event:{afterChange:function(e,n,r){return t.selectedFilter=$(n.$slides.get(r)).data("value")}}},t.appendFormatListener=function(){$(".f_format").on("afterChange",function(e,n,r){return t.selectedFormat=$(n.$slides.get(r)).data("value")})},t.appendFilterListener=function(){$(".m_filter").on("afterChange",function(e,n,r){return t.selectedFilter=$(n.$slides.get(r)).data("value")})},t.selectTab=function(e){return t.selectedTab=e},t.nextSubSelection=function(){return $(".filter-container").slick("slickNext"),!1},t.previewsSubSelection=function(){return $(".filter-container").slick("slickPrev"),!1},t.deleteFile=function(s){var l;return t.toggleShareDialog(),l=r["delete"](o.installation.httpurl+"api/v1/scans/"+a.getScanId()+"/files/"+s),l.then(function(r){return e.info(r.data),t.getScans(),"SCAN_DELETED"===r.data.response&&(i.info('Scan "'+r.data.scan_id+'" deleted'),a.setScanId(null),t.setScanLoaded(!1),n.$broadcast("clearView")),{"else":i.info('File "'+s+'" deleted')}})},t.deleteScan=function(){var s;return t.toggleShareDialog(),s=r["delete"](o.installation.httpurl+"api/v1/delete/"+a.getScanId()),s.then(function(t){return e.info(t.data),i.info("Scan "+a.getScanId()+" deleted"),a.setScanId(null),n.$broadcast("clearView")})},t.loadPointCloud=function(e){return t.toggleShareDialog(),t.scanComplete=!1,toastr.info("Loading file..."),t.loadPLY(e)},t.runMeshing=function(){return t.toggleShareDialog(),a.runMeshing(a.getScanId(),t.selectedFilter,t.selectedFormat)}}])}.call(this),function(){var e;e="fabscan.controller.FSStartupController",angular.module(e,[]).controller(e,["$log","$scope","$rootScope","fabscan.services.FSEnumService","fabscan.services.FSScanService","fabscan.services.FSMessageHandlerService",function(){}])}.call(this);
>>>>>>> d40ca7112543dd671c58d91732615f88abd6f1fa
