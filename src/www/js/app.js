(function() {
  /* */
  //#######################################################################
  //#######################################################################
  var m, mods;

  // Wire modules together
  /* */
  mods = [
    'common.services.envProvider',
    'common.filters.currentStateFilter',
    'common.filters.toLabelFilter',
    'common.filters.toResolutionValue',
    'fabscan.directives.FSWebglDirective',
    'fabscan.directives.FSMJPEGStream',
    'fabscan.directives.FSModalDialog',
    'fabscan.directives.text',
    'fabscan.services.FSMessageHandlerService',
    'fabscan.services.FSEnumService',
    'fabscan.services.FSWebsocketConnectionFactory',
    'fabscan.services.FSScanService',
    'fabscan.services.FSi18nService',
    'common.filters.scanDataAvailableFilter',
    'fabscan.directives.onSizeChanged',
    'common.services.Configuration',
    'common.services.toastrWrapperSvc',
    'fabscan.controller.FSPreviewController',
    'fabscan.controller.FSAppController',
    'fabscan.controller.FSNewsController',
    'fabscan.controller.FSSettingsController',
    'fabscan.controller.FSScanController',
    'fabscan.controller.FSLoadingController',
    'fabscan.controller.FSShareController',
    'ngSanitize',
    'ngTouch',
    'ngCookies',
    '720kb.tooltips',
    'ngProgress',
    'vr.directives.slider',
    'slickCarousel' //#######################################################################
//#######################################################################
//#######################################################################
//#######################################################################
  ];

  /* */
  // Declare routes
  /* */

  //routesConfigFn = ($routeProvider)->

  //	$routeProvider.otherwise({redirectTo: '/'})
  /* */
  // Create and bootstrap app module
  /* */
  //'ng.jsoneditor'
  m = angular.module('fabscan', mods);

  //m.config ['$routeProvider', routesConfigFn]
  m.config([
    'common.services.envProvider',
    function(envProvider) {
      // Allows the environment provider to run whatever config block it wants.
      if (envProvider.appConfig != null) {
        return envProvider.appConfig();
      }
    }
  ]);

  m.run([
    'common.services.env',
    function(env) {
      // Allows the environment service to run whatever app run block it wants.
      if (env.appRun != null) {
        return env.appRun();
      }
    }
  ]);

  m.config([
    '$httpProvider',
    function($httpProvider) {
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

  angular.module(name, []).directive('mjpeg', function() {
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
            iframeHtml = '<html><head><base target="_parent" /><style type="text/css">html, body { margin: 0; padding: 0; height: 100%; width: 100%; }</style><script> function resizeParent() { var ifs = window.top.document.getElementsByTagName("iframe"); for (var i = 0, len = ifs.length; i < len; i++) { var f = ifs[i]; var fDoc = f.contentDocument || f.contentWindow.document; if (fDoc === document) { f.height = 0; f.height = document.body.scrollHeight; } } }</script></head><body onresize="resizeParent()"><img src=\"' + newVal + '\" style="width: 100%; height: auto" onload="resizeParent()" /></body></html>';
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
  });

}).call(this);

(function() {
  var name;

  name = 'fabscan.directives.FSModalDialog';

  angular.module(name, []).directive("modalDialog", [
    '$log',
    function($log) {},
    {
      restrict: 'E',
      scope: {
        show: '='
      },
      replace: true,
      transclude: true,
      link: function(scope,
    element,
    attrs) {
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
      template: "<div class='ng-modal' ng-show='show'> <div class='ng-modal-overlay' ng-click='hideModal()'></div> <div class='ng-modal-dialog' ng-style='dialogStyle'> <div class='ng-modal-close' ng-click='hideModal()'>X</div> <div class='ng-modal-dialog-content' ng-transclude></div> </div> </div>"
    }
  ]);

}).call(this);

(function() {
  var name;

  name = 'fabscan.directives.slick';

  angular.module(name, []).directive("slickSlider", [
    '$log',
    '$timeout',
    function($log,
    $timeout) {
      return {
        restrict: 'A',
        link: function(scope,
    element,
    attrs) {
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

  name = 'fabscan.directives.text';

  angular.module(name, []).directive("text", [
    'fabscan.services.FSi18nService',
    function(i18n) {
      return {
        restrict: 'A',
        link: function(scope,
    element,
    attrs) {
          var renderText;
          renderText = function() {
            return element[0].textContent = i18n.formatText(attrs.text);
          };
          scope.$watch(function() {
            return attrs.text;
          },
    function() {
            return renderText();
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
    '$log',
    '$rootScope',
    '$http',
    'fabscan.services.FSEnumService',
    'common.services.Configuration',
    function($log,
    $rootScope,
    $http,
    FSEnumService,
    Configuration) {
      var postLink;
      return {
        restrict: "A",
        //scope:
        //  width: "="
        //  height: "="
        //  fillcontainer: "="
        //  scale: "="
        //  materialType: "="
        //  newPoints: "="
        link: postLink = function(scope,
    element,
    attrs) {
          var camera,
    cameraTarget,
    colors,
    contH,
    contW,
    controls,
    currentPointcloudAngle,
    current_point,
    materials,
    mesh,
    mouseX,
    mouseY,
    mousedown,
    pointcloud,
    positions,
    rad,
    renderer,
    scanLoaded,
    scene,
    turntable,
    turntable_radius,
    turntable_thickness,
    windowHalfX,
    windowHalfY;
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
          turntable = void 0;
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
          turntable_radius = 70;
          turntable_thickness = 5;
          $rootScope.$on('clearcanvas',
    function() {
            $log.info("view cleared");
            return scope.clearView();
          });
          scope.$on(FSEnumService.events.ON_STATE_CHANGED,
    function(events,
    data) {
            if (data['state'] === FSEnumService.states.SCANNING) {
              return scope.clearView();
            }
          });
          scope.$on(FSEnumService.events.ON_INFO_MESSAGE,
    function(event,
    data) {
            if (data['message'] === 'SCANNING_TEXTURE' || data['message'] === 'START_CALIBRATION') {
              scene.remove(turntable);
            }
            if (data['message'] === 'SCANNING_OBJECT') {
              if (!scene.getObjectByName('turntable')) {
                scene.add(turntable);
              }
            }
            if (data['message'] === 'SCAN_CANCELED' || data['message'] === 'FINISHED_CALIBRATION') {
              scope.clearView();
              if (!scene.getObjectByName('turntable')) {
                scene.add(turntable);
              }
            }
            if (data['message'] === 'SCAN_COMPLETE') {
              scope.createPreviewImage(data['scan_id']);
              scope.scanComplete = true;
              return scope.currentPointcloudAngle = 0;
            }
          });
          scope.init = function() {
            var axes,
    geometry,
    material,
    plane;
            // Camera
            //camera = new THREE.PerspectiveCamera(48, window.innerWidth / window.innerHeight, 1, 4800)
            //camera.position.z = 1380
            //camera.position.y = 850

            //camera.rotation.order = 'YXZ'
            //camera.position.set(0,0,1500)
            current_point = 0;
            camera = new THREE.PerspectiveCamera(48.8,
    window.innerWidth / window.innerHeight,
    1,
    1000);
            camera.position.z = 180;
            camera.position.y = 40;
            scene = new THREE.Scene();
            scene.fog = new THREE.Fog(0x72645b,
    200,
    600);
            plane = new THREE.Mesh(new THREE.PlaneBufferGeometry(2000,
    2000),
    new THREE.MeshPhongMaterial({
              ambient: 0x999999,
              color: 0x999999,
              specular: 0x101010
            }));
            plane.rotation.x = -Math.PI / 2;
            plane.position.y = -2 * turntable_thickness;
            scene.add(plane);
            plane.receiveShadow = true;
            scene.add(new THREE.AmbientLight(0x777777));
            //light = new THREE.DirectionalLight( 0xffffff );
            //light.position.set( 0, 1, 1 ).normalize();
            //scene.add(light);
            scope.addShadowedLight(1,
    1,
    1,
    0xffffff,
    0.35);
            scope.addShadowedLight(0.5,
    1,
    -1,
    0xffaa00,
    1);
            //scene.add( new THREE.HemisphereLight( 0x443333, 0x111122 ) );

            //addShadowedLight( 1, 1, 1, 0xffffff, 1.35 );
            //addShadowedLight( 0.5, 1, -1, 0xffaa00, 1 );
            //Grid
            //gridXZ = new THREE.GridHelper(4000, 100)

            //scene.add(gridXZ)
            axes = new THREE.AxisHelper(10);
            geometry = new THREE.CylinderGeometry(turntable_radius,
    turntable_radius,
    turntable_thickness,
    32);
            material = new THREE.MeshPhongMaterial({
              color: 0xd3d2c9
            });
            turntable = new THREE.Mesh(geometry,
    material);
            turntable.position.y -= turntable_thickness;
            turntable.name = "turntable";
            scene.add(turntable);
            renderer = new THREE.WebGLRenderer({
              preserveDrawingBuffer: true
            });
            //renderer.setColor(0x000000, 0)
            //renderer.setSize( window.innerWidth, window.innerHeight )
            //renderer.setSize(contW,contH-4)
            //renderer = new THREE.WebGLRenderer( { antialias: true } )
            renderer.setClearColor(scene.fog.color);
            //renderer.setPixelRatio( window.devicePixelRatio )
            renderer.setSize(window.innerWidth,
    window.innerHeight);
            renderer.gammaInput = true;
            renderer.gammaOutput = true;
            renderer.shadowMapEnabled = true;
            renderer.shadowMapCullFace = THREE.CullFaceBack;
            // element is provided by the angular directive
            element[0].appendChild(renderer.domElement);
            window.addEventListener("resize",
    scope.onWindowResize,
    false);
            window.addEventListener("DOMMouseScroll",
    scope.onMouseWheel,
    false);
            window.addEventListener("mousewheel",
    scope.onMouseWheel,
    false);
            document.addEventListener("keydown",
    scope.onKeyDown,
    false);
            element[0].addEventListener("mousemove",
    scope.onMouseMove,
    false);
            element[0].addEventListener("mousedown",
    scope.onMouseDown,
    false);
            element[0].addEventListener("mouseup",
    scope.onMouseUp,
    false);
          };
          // ----------------------------------
          // Controls
          // ----------------------------------

          // -----------------------------------
          // Event listeners
          // -----------------------------------
          scope.createPreviewImage = function(id) {
            var screenshot;
            screenshot = renderer.domElement.toDataURL('image/png');
            return $http.post(Configuration.installation.apiurl + "api/v1/scans/" + id + "/previews",
    {
              image: screenshot
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
              d = ((evt.movementX > 0) ? 0.1 : -0.1);
              if (pointcloud && scope.scanLoaded) {
                pointcloud.rotation.z += d;
              }
              if (pointcloud && scope.scanComplete) {
                pointcloud.rotation.y += d;
              }
              if (mesh && scope.scanLoaded) {
                return mesh.rotation.z += d;
              }
            }
          };
          //scope.onMouseWheel = (evt) ->

          //  d = ((if (typeof evt.wheelDelta isnt "undefined") then (-evt.wheelDelta) else evt.detail))
          //  d =  ((if (d > 0) then 0.1 else -0.1))
          //console.log d
          //cPos = camera.position
          //return  if isNaN(cPos.x) or isNaN(cPos.y) or isNaN(cPos.y)
          //  if pointcloud
          //    if scope.scanComplete
          //        pointcloud.rotation.y +=d
          //    else
          //        pointcloud.rotation.z += d

          // Your zomm limitation
          // For X axe you can add anothers limits for Y / Z axes
          //return  if cPos.z > 50 or cPos.z < -50
          //mb = (if d > 0 then 1.1 else 0.9)
          //cPos.x = cPos.x * mb
          //cPos.y = cPos.y * mb
          //cPos.z = cPos.z * mb
          //  return

          // Handle colors and pointsize
          scope.onKeyDown = function(evt) {
            var material;
            if (evt.keyCode === 189 || evt.keyCode === 109) {
              // Increase/decrease point size
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
            // Re-render the scene
            material = new THREE.ParticleBasicMaterial({
              size: pointSize,
              vertexColors: true
            });
            pointcloud = new THREE.ParticleSystem(geometry,
    material);
            scene = new THREE.Scene();
            //scene.fog = new THREE.FogExp2(0x000000, 0.0009)
            scene.add(pointcloud);
            return scope.render();
          };
          // -----------------------------------
          // Updates
          // -----------------------------------
          scope.resizeCanvas = function() {
            contW = (scope.fillcontainer ? element[0].clientWidth : scope.width);
            contH = scope.height;
            windowHalfX = contW / 2;
            windowHalfY = contH / 2;
            camera.aspect = contW / contH;
            camera.updateProjectionMatrix();
            renderer.setSize(contW,
    contH);
          };
          scope.resizeObject = function() {};
          //icosahedron.scale.set scope.scale, scope.scale, scope.scale
          //shadowMesh.scale.set scope.scale, scope.scale, scope.scale
          scope.changeMaterial = function() {};
          //icosahedron.material = materials[scope.materialType]
          scope.Float32Concat = function(first,
    second) {
            var firstLength,
    result;
            firstLength = first.length;
            result = new Float32Array(firstLength + second.length);
            result.set(first);
            result.set(second,
    firstLength);
            return result;
          };
          scope.addShadowedLight = function(x,
    y,
    z,
    color,
    intensity) {
            var d,
    directionalLight;
            directionalLight = new THREE.DirectionalLight(color,
    intensity);
            directionalLight.position.set(x,
    y,
    z);
            scene.add(directionalLight);
            directionalLight.castShadow = true;
            // directionalLight.shadowCameraVisible = true;
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
          scope.renderMesh = function(meshFormat) {
            var material;
            scope.clearView();
            scope.objectGeometry.computeFaceNormals();
            if (meshFormat === 'stl') {
              material = new THREE.MeshPhongMaterial({
                color: 0x0000FF,
                specular: 0x111111,
                shininess: 100
              });
            } else {
              material = new THREE.MeshBasicMaterial({
                shininess: 200,
                wireframe: false,
                vertexColors: THREE.FaceColors
              });
            }
            mesh = new THREE.Mesh(scope.objectGeometry,
    material);
            mesh.position.set(0,
    -0.25,
    0);
            mesh.rotation.set(-Math.PI / 2,
    0,
    0);
            if (meshFormat === 'stl') {
              mesh.castShadow = true;
              mesh.receiveShadow = true;
            }
            return scene.add(mesh);
          };
          scope.renderPLY = function() {
            var material;
            pointcloud = new THREE.Object3D;
            material = new THREE.PointsMaterial({
              size: 0.5,
              vertexColors: THREE.FaceColors
            });
            pointcloud = new THREE.Points(scope.objectGeometry,
    material);
            pointcloud.rotation.set(-Math.PI / 2,
    0,
    0);
            return scene.add(pointcloud);
          };
          scope.renderObjectAsType = function(type) {
            if (type === "MESH") {
              scope.clearView();
              scope.renderMesh('ply');
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
            loader.load(file,
    function(objectGeometry) {
              //scene.add( new THREE.Mesh( geometry ) )
              scope.objectGeometry = objectGeometry;
              if (file.indexOf("mesh") > -1) {
                scope.renderMesh('stl');
              }
              return scope.scanLoaded = true;
            });
            return loader.addEventListener('progress',
    function(item) {
              scope.progressHandler(item);
              return $log.info("Not implemented yet");
            });
          };
          scope.loadPLY = function(file) {
            var loader;
            scope.clearView();
            scope.scanComplete = false;
            loader = new THREE.PLYLoader();
            loader.useColor = true;
            loader.colorsNeedUpdate = true;
            loader.addEventListener('progress',
    function(item) {
              return scope.progressHandler(item);
            });
            return loader.load(file,
    function(objectGeometry) {
              scope.objectGeometry = objectGeometry;
              if (file.indexOf("mesh") > -1) {
                scope.renderMesh();
              } else {
                scope.renderPLY();
              }
            });
          };
          scope.addPoints = function(points,
    progress,
    resolution) {
            var color,
    degree,
    geometry,
    i,
    material,
    new_colors,
    new_positions;
            scope.scanComplete = false;
            if (points && (points.length > 0)) {
              if (pointcloud) {
                currentPointcloudAngle = pointcloud.rotation.y;
                scene.remove(pointcloud);
              } else {
                currentPointcloudAngle = 90 * (Math.PI / 180);
              }
              new_positions = new Float32Array(points.length * 3);
              new_colors = new Float32Array(points.length * 3);
              i = 0;
              while (i < points.length) {
                new_positions[3 * i] = parseFloat(points[i]['x'] * -1);
                new_positions[3 * i + 1] = parseFloat(points[i]['y']);
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
                positions = scope.Float32Concat(positions,
    new_positions);
                colors = scope.Float32Concat(colors,
    new_colors);
              }
              geometry = new THREE.BufferGeometry();
              geometry.dynamic = true;
              geometry.addAttribute('position',
    new THREE.BufferAttribute(positions,
    3));
              geometry.addAttribute('color',
    new THREE.BufferAttribute(colors,
    3));
              if (!pointcloud) {
                material = new THREE.PointsMaterial({
                  size: 0.5,
                  vertexColors: THREE.VertexColors
                });
                pointcloud = new THREE.Points(geometry,
    material);
              } else {
                pointcloud.geometry.dispose();
                pointcloud.geometry = geometry;
              }
              degree = 360 / resolution;
              $log.info(degree);
              scope.rad = degree * (Math.PI / 180);
              scene.add(pointcloud);
              if (pointcloud) {
                return pointcloud.rotation.y = scope.rad;
              }
            }
          };
          //  $log.info currentPointcloudAngle - scope.rad

          //while i < points.length
          //point = new THREE.Vector3(parseFloat(points[i].x), parseFloat(points[i].z)+450, parseFloat(points[i].y))
          //pointcloud.geometry.vertices.push(point)
          //pointcloud.geometry.dispose()
          //_points[current_point] = points
          //i++
          //current_point++

          //if progress == resolution
          //scope.createScreenShot()
          //pointcloudRotation = angle
          scope.clearView = function() {
            if (pointcloud) {
              positions = void 0;
              colors = void 0;
              scene.remove(pointcloud);
              return scene.remove(mesh);
            }
          };
          // -----------------------------------
          // Draw and Animate
          // -----------------------------------
          scope.animate = function() {
            requestAnimationFrame(scope.animate);
            scope.render();
          };
          scope.render = function() {
            //camera.position.x += (mouseX - camera.position.x) * 0.05

            //camera.position.y += ( - mouseY - camera.position.y ) * 0.05;

            //camera.lookAt scene.position

            //camera.lookAt scene
            //pointcloud.add( camera )
            //camera.position.set( 15, 0, 0 );
            //camera.lookAt( new THREE.Vector3( 0, 0, 0 ) );
            //pointcloud.rotation.y
            //camera.lookAt( cameraTarget )
            renderer.render(scene,
    camera);
          };
          // -----------------------------------
          // Watches
          // -----------------------------------
          //controls.update()
          scope.$watch("newPoints",
    function(newValue,
    oldValue) {
            if (newValue !== []) {
              if (newValue !== oldValue) {
                scope.addPoints(newValue);
              }
            }
          });
          scope.$watch("fillcontainer + width + height",
    function() {
            scope.resizeCanvas();
          });
          scope.$watch("scale",
    function() {
            scope.resizeObject();
          });
          scope.$watch("materialType",
    function() {});
          // Begin
          //scope.changeMaterial()
          scope.init();
          scope.animate();
        }
      };
    }
  ]);

}).call(this);

(function() {
  var name;

  name = 'fabscan.directives.onSizeChanged';

  angular.module(name, []).directive('onSizeChanged', [
    '$window',
    function($window) {
      return {
        restrict: 'A',
        scope: {
          onSizeChanged: '&'
        },
        link: function(scope,
    $element,
    attr) {
          var cacheElementSize,
    element,
    onWindowResize;
          element = $element[0];
          cacheElementSize = function(scope,
    element) {
            scope.cachedElementWidth = element.offsetWidth;
            scope.cachedElementHeight = element.offsetHeight;
          };
          onWindowResize = function() {
            var expression,
    isSizeChanged;
            isSizeChanged = scope.cachedElementWidth !== element.offsetWidth || scope.cachedElementHeight !== element.offsetHeight;
            if (isSizeChanged) {
              expression = scope.onSizeChanged();
              expression();
            }
          };
          cacheElementSize(scope,
    element);
          $window.addEventListener('resize',
    onWindowResize);
        }
      };
    }
  ]);

}).call(this);

(function() {
  /*
  Takes a string and makes it lowercase
  Example of a 'common' filter that can be shared by all views
  */
  var name;

  name = 'common.filters.currentStateFilter';

  // Note that for filters I keep the name SHORT
  // and they do not match the name of the module
  angular.module(name, []).filter('currentState', [
    '$log',
    'fabscan.services.FSScanService',
    function($log,
    FSScanService) {
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

(function() {
  /*
  Takes a string and makes it lowercase
  Example of a 'common' filter that can be shared by all views
  */
  var name;

  name = 'common.filters.scanDataAvailableFilter';

  // Note that for filters I keep the name SHORT
  // and they do not match the name of the module
  angular.module(name, []).filter('scanDataAvailable', [
    '$log',
    'fabscan.services.FSScanService',
    function($log,
    FSScanService) {
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

  // Note that for filters I keep the name SHORT
  // and they do not match the name of the module
  angular.module(name, []).filter('toLabel', [
    '$log',
    function($log) {
      return function(str) {
        var date,
    label_parts,
    time;
        label_parts = str.split("-");
        date = label_parts[0];
        time = label_parts[1];
        date = date.slice(0,
    4) + "-" + date.slice(4);
        date = date.slice(0,
    7) + "-" + date.slice(7);
        time = time.slice(0,
    2) + ":" + time.slice(2);
        time = time.slice(0,
    5) + ":" + time.slice(5);
        return date + " " + time;
      };
    }
  ]);

}).call(this);

(function() {
  /*
  Takes a string and makes it lowercase
  Example of a 'common' filter that can be shared by all views
  */
  var name;

  name = 'common.filters.toLowerFilter';

  // Note that for filters I keep the name SHORT
  // and they do not match the name of the module
  angular.module(name, []).filter('toLower', [
    '$log',
    function($log) {
      return function(str) {
        return str.toLowerCase();
      };
    }
  ]);

}).call(this);

(function() {
  var name;

  name = 'common.filters.toResolutionValue';

  // Note that for filters I keep the name SHORT
  // and they do not match the name of the module
  angular.module(name, []).filter('toResolutionValue', [
    '$log',
    function($log) {
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
    '$log',
    '$location',
    function($log,
    $location) {
      var config,
    host,
    http,
    localDebug,
    ws;
      localDebug = $location.host() === 'localhost';
      config = null;
      host = $location.host();
      http = 'http';
      ws = 'ws';
      //console.log($location.protocol())
      if ($location.protocol() === 'https') {
        http = 'https';
        ws = 'wss';
      }
      if (localDebug) {
        config = {
          installation: {
            host: "fabscanpi.local",
            websocketurl: ws + '://fabscanpi.local/websocket',
            httpurl: http + '://fabscanpi.local/',
            newsurl: http + '://fabscanpi-server.readthedocs.io/en/latest/news/',
            apiurl: http + '://fabscanpi.local/'
          }
        };
      } else {
        config = {
          installation: {
            host: host,
            websocketurl: ws + '://' + host + '/websocket',
            httpurl: http + '://' + host + ':8080/',
            newsurl: 'https://fabscanpi-server.readthedocs.io/en/latest/news/',
            apiurl: http + '://' + host + '/'
          }
        };
      }
      return config;
    }
  ]);

}).call(this);

(function() {
  /*
  Example of a service shared across views.
  Wrapper around the data layer for the app. 
  */
  var DataSvc, name;

  name = 'common.services.dataSvc';

  DataSvc = class DataSvc {
    constructor($log1, $http1, env1) {
      this.$log = $log1;
      this.$http = $http1;
      this.env = env1;
    }

    _get(relPath) {
      return this.$http.get(`${this.env.serverUrl}/${relPath}`);
    }

    getPeople() {
      return this._get('people');
    }

    getPerson(id) {
      return this._get(`person/${id}`);
    }

  };

  angular.module(name, []).factory(name, [
    '$log',
    '$http',
    'common.services.env',
    function($log,
    $http,
    env) {
      return new DataSvc($log,
    $http,
    env);
    }
  ]);

}).call(this);

(function() {
  /*
  DEV
  */
  var Environment, EnvironmentProvider, mod, modName, providerName;

  providerName = 'common.services.env'; // angular adds the 'Provider' suffix for us.

  modName = `${providerName}Provider`;

  Environment = (function() {
    class Environment {};

    Environment.prototype.env = 'DEV';

    return Environment;

  }).call(this);

  EnvironmentProvider = class EnvironmentProvider {
    $get() {
      return new Environment();
    }

  };

  mod = angular.module(modName, []);

  mod.provider(providerName, new EnvironmentProvider());

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
      SETTINGS: 'SETTINGS',
      CALIBRATING: 'CALIBRATING',
      UPGRADING: 'UPGRADING'
    };
    FSEnumService.commands = {
      SCAN: 'SCAN',
      START: 'START',
      STOP: 'STOP',
      CALIBRATE: 'CALIBRATE',
      UPDATE_SETTINGS: 'UPDATE_SETTINGS',
      MESHING: 'MESHING',
      UPGRADE_SERVER: 'UPGRADE_SERVER',
      RESTART_SERVER: 'RESTART_SERVER',
      HARDWARE_TEST_FUNCTION: 'HARDWARE_TEST_FUNCTION'
    };
    return FSEnumService;
  });

}).call(this);

(function() {
  var name;

  name = 'fabscan.services.FSi18nService';

  angular.module(name, []).factory(name, [
    '$window',
    function($window) {
      var service;
      service = {};
      service.formatText = function(key,
    values = {}) {
        var catalog,
    catalogId,
    textId;
        [catalogId,
    textId] = key.split(".");
        if (catalogId && textId) {
          if (catalogId in $window.i18n) {
            catalog = $window.i18n[catalogId];
            if (textId in catalog) {
              return catalog[textId](values);
            }
          }
        }
        return key;
      };
      return service;
    }
  ]);

}).call(this);

(function() {
  var name;

  name = 'fabscan.services.FSMessageHandlerService';

  angular.module(name, []).factory(name, [
    '$log',
    '$timeout',
    '$rootScope',
    '$http',
    'fabscan.services.FSWebsocketConnectionFactory',
    'common.services.Configuration',
    function($log,
    $timeout,
    $rootScope,
    $http,
    FSWebsocketConnectionFactory,
    Configuration) {
      var FSMessageHandlerService,
    socket;
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
          $rootScope.$broadcast("CONNECTION_STATE_CHANGED",
    true);
          return console.log('Websocket connected to ' + socket.url);
        };
        socket.onerror = function(event) {
          return console.error(event);
        };
        socket.onclose = function(event) {
          scope.isConnected = false;
          socket = null;
          $rootScope.$broadcast("CONNECTION_STATE_CHANGED",
    scope.isConnected);
          $timeout(function() {
            return FSMessageHandlerService.connectToScanner(scope);
          },
    100);
          return console.log("Connection closed");
        };
        return socket.onmessage = function(event) {
          var message;
          message = jQuery.parseJSON(event.data);
          $log.info(message['data']);
          return $rootScope.$broadcast(message['type'],
    message['data']);
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
    '$log',
    '$rootScope',
    'fabscan.services.FSEnumService',
    'fabscan.services.FSMessageHandlerService',
    function($log,
    $rootScope,
    FSEnumService,
    FSMessageHandlerService) {
      var service;
      service = {};
      service.state = FSEnumService.states.IDLE;
      service.scanId = null;
      service.startTime = null;
      service.initStartTime = function() {
        return service.startTime = Date.now();
      };
      service.setStartTime = function(time) {
        return service.startTime = time;
      };
      service.getStartTime = function() {
        return service.startTime;
      };
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
        service.initStartTime();
        // FIXME: ( or find better solution )
        // needed to be done here, cause raspberry has not a real time clock,
        // when no internet connection is availabale on the fabscan the time
        // will be set (default) to 1970, this leads to a wrong calculation...
        message = {};
        message = {
          event: FSEnumService.events.COMMAND,
          data: {
            command: FSEnumService.commands.START,
            startTime: service.getStartTime()
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
        //settings: settings
        return FSMessageHandlerService.sendData(message);
      };
      service.upgradeServer = function() {
        var message;
        $log.debug("Upgrade Server called.");
        message = {};
        message = {
          event: FSEnumService.events.COMMAND,
          data: {
            command: FSEnumService.commands.UPGRADE_SERVER
          }
        };
        return FSMessageHandlerService.sendData(message);
      };
      service.restartServer = function() {
        var message;
        message = {};
        message = {
          event: FSEnumService.events.COMMAND,
          data: {
            command: FSEnumService.commands.RESTART_SERVER
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
      service.startCalibration = function() {
        var message;
        message = {};
        service.initStartTime();
        message = {
          event: FSEnumService.events.COMMAND,
          data: {
            command: FSEnumService.commands.CALIBRATE,
            startTime: service.getStartTime()
          }
        };
        FSMessageHandlerService.sendData(message);
        return $rootScope.$broadcast(FSEnumService.commands.CALIBRATE);
      };
      service.runMeshing = function(scan_id,
    filter,
    format,
    file) {
        var message;
        message = {};
        message = {
          event: FSEnumService.events.COMMAND,
          data: {
            command: FSEnumService.commands.MESHING,
            scan_id: scan_id,
            file: file,
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
      //data:
      //command: FSEnumService.commands.GET_SETTINGS
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
  /*
  Example of how to wrap a 3rd party library, allowing it to be injectable instead of using the global var
  */
  var name;

  name = 'common.services.toastrWrapperSvc';

  angular.module(name, []).factory(name, function() {
    // override some default settings
    // window.toastr.options.timeOut = 1000
    //window.toastr.options.
    window.toastr.options.newestOnTop = true;
    window.toastr.options.positionClass = "toast-top-left";
    return window.toastr;
  });

}).call(this);

(function() {
  var name;

  name = 'fabscan.controller.FSAppController';

  angular.module(name, []).controller(name, [
    '$log',
    '$scope',
    '$timeout',
    '$http',
    '$rootScope',
    'ngProgress',
    'common.services.toastrWrapperSvc',
    'fabscan.services.FSMessageHandlerService',
    'fabscan.services.FSEnumService',
    'fabscan.services.FSScanService',
    'fabscan.services.FSi18nService',
    function($log,
    $scope,
    $timeout,
    $http,
    $rootScope,
    ngProgress,
    toastr,
    FSMessageHandlerService,
    FSEnumService,
    FSScanService,
    FSi18nService) {
      $scope.streamUrl = " ";
      $scope.settings = {};
      $scope.scanComplete = false;
      $scope.scanLoaded = false;
      $scope.remainingTime = [];
      $scope.server_version = void 0;
      $scope.firmware_version = void 0;
      $scope.scanLoading = false;
      $scope.appIsInitialized = false;
      $scope.isCalibrating = false;
      $scope.appIsUpgrading = false;
      $scope.isConnected = false;
      $scope.initError = false;
      $timeout((function() {
        $scope.appInitError();
      }),
    60000);
      $scope.appInitError = function() {
        return $scope.initError = true;
      };
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
      $scope.upgradeServer = function() {
        return FSScanService.upgradeServer();
      };
      $scope.$on("CONNECTION_STATE_CHANGED",
    function(event,
    connected) {
        $log.info("Connected: " + connected);
        $scope.isConnected = connected;
        //$scope.appIsInitialized = true
        if (!connected) {
          $scope.appIsInitialized = false;
        }
        return $scope.$apply();
      });
      $scope.$on(FSEnumService.events.ON_CLIENT_INIT,
    function(event,
    data) {
        var _settings;
        $log.info("Initing");
        $scope.appIsInitialized = true;
        $scope.remainingTime = [];
        $log.info("State: " + data['state']);
        document.title = "FabScanPi " + data['server_version'];
        $scope.server_version = data['server_version'];
        $scope.firmware_version = data['firmware_version'];
        if (data['upgrade']['available']) {
          toastr.info('Click here for upgrade! ',
    'Version ' + data['upgrade']['version'] + ' now available',
    {
            timeOut: 0,
            closeButton: true,
            onclick: function() {
              $scope.upgradeServer();
            }
          });
        }
        _settings = data['settings'];
        //_settings.resolution *=-1
        angular.copy(_settings,
    $scope.settings);
        FSScanService.setScannerState(data['state']);
        $scope.appIsUpgrading = data['state'] === FSEnumService.states.UPGRADING;
        if (data['state'] === FSEnumService.states.IDLE) {
          $scope.displayNews(true);
        }
        $log.debug("WebSocket connection ready...");
        //toastr.info(FSi18nService.translateKey('main','CONNECTED_TO_SERVER'))
        return $scope.$apply();
      });
      $scope.displayNews = function(value) {
        return $scope.showNews = value;
      };
      $scope.$on(FSEnumService.events.ON_STATE_CHANGED,
    function(event,
    data) {
        $scope.showNews = false;
        $log.info("NEW STATE: " + data['state']);
        FSScanService.setScannerState(data['state']);
        $log.info(data);
        if (data['state'] === FSEnumService.states.IDLE) {
          ngProgress.complete();
        }
        if (data['state'] === FSEnumService.states.CALIBRATING) {
          $scope.isCalibrating = true;
        } else {
          $scope.isCalibrating = false;
        }
        //$scope.$broadcast('refreshSlider');
        return $scope.$apply();
      });
      $scope.$on(FSEnumService.events.ON_INFO_MESSAGE,
    function(event,
    data) {
        var message;
        $log.info(data['message']);
        message = FSi18nService.formatText('main.' + data['message']);
        switch (data['level']) {
          case "info":
            toastr.info(message,
    {
              timeOut: 5000
            });
            break;
          case "warn":
            toastr.warning(message);
            break;
          case "error":
            toastr.error(message,
    {
              timeOut: 0
            });
            break;
          case "success":
            toastr.success(message);
            break;
          default:
            toastr.info(message);
        }
        if (data['message'] === "RESTARTING_SERVER") {
          location.reload();
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
    '$log',
    '$scope',
    '$rootScope',
    'fabscan.services.FSScanService',
    'fabscan.services.FSEnumService',
    'common.services.Configuration',
    function($log,
    $scope,
    $rootScope,
    FSScanService,
    FSEnum,
    Configuration) {
      $scope.loadPointCloud = function(pointcloud,
    id) {
        $scope.setScanIsLoading(true);
        $scope.setScanIsComplete(false);
        $scope.toggleLoadDialog();
        FSScanService.setScanId(id);
        $scope.setScanLoaded(false);
        toastr.info("Loading scanned Pointcloud " + id);
        return $scope.loadPLY(pointcloud);
      };
      return $scope.loadMesh = function(mesh,
    id) {};
    }
  ]);

}).call(this);

(function() {
  var name;

  name = "fabscan.controller.FSNewsController";

  angular.module(name, []).controller(name, [
    '$log',
    '$scope',
    '$http',
    '$timeout',
    '$cookies',
    '$q',
    'common.services.Configuration',
    function($log,
    $scope,
    $http,
    $timeout,
    $cookies,
    $q,
    configuration) {
      var deferred,
    hashCode,
    timeoutPromise;
      hashCode = function(str) {
        var char,
    hash,
    i;
        hash = 0;
        if (str.length === 0) {
          return hash;
        }
        i = 0;
        while (i < str.length) {
          char = str.charCodeAt(i);
          hash = (hash << 5) - hash + char;
          hash = hash & hash;
          // Convert to 32bit integer
          i++;
        }
        return hash;
      };
      timeoutPromise = $timeout((function() {
        //aborts the request when timed out
        deferred.resolve();
        console.log('News request timeout...');
        $scope.displayNews(false);
      }),
    1);
      deferred = $q.defer();
      $scope.news = "No news available.";
      return $http({
        method: 'GET',
        url: configuration.installation.newsurl,
        timeout: deferred.promise
      }).success(function(data,
    status,
    headers,
    config) {
        //    newsHASH = hashCode(data)
        //    if newsHASH == $cookies.newsHASH
        //      $log.debug("Nothing new here")
        //    else
        //      $log.debug("Some news are available")

        //$log.info("News Hash "+hashCode(data))
        $scope.news = data;
        return $timeout.cancel(timeoutPromise);
      }).error(function(data,
    status,
    headers,
    config) {
        return $scope.news = "Error retrieving news.";
      });
    }
  ]);

}).call(this);

(function() {
  var name,
    indexOf = [].indexOf;

  name = "fabscan.controller.FSPreviewController";

  angular.module(name, []).controller(name, [
    '$log',
    '$scope',
    '$rootScope',
    '$http',
    'ngProgress',
    'common.services.Configuration',
    'fabscan.services.FSEnumService',
    'fabscan.services.FSScanService',
    function($log,
    $scope,
    $rootScope,
    $http,
    ngProgress,
    Configuration,
    FSEnum,
    FSScanService) {
      var median,
    resetSate,
    startStream,
    stopStream;
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
      $scope.showStream = false;
      $scope.startTime = null;
      $scope.sampledRemainingTime = 0;
      $scope.remainingTimeString = "0 minutes 0 seconds";
      stopStream = function() {
        $scope.showStream = false;
        $scope.streamUrl = "";
        return $scope.$apply();
      };
      startStream = function() {};
      //$scope.streamUrl = Configuration.installation.apiurl+'api/v1/streams/?type=textures'
      //$scope.showStream = true
      //$scope.$apply()
      resetSate = function() {
        $scope.remainingTime = [];
        $scope.showStream = false;
        $scope.startTime = null;
        $scope.progress = 0;
        $scope.sampledRemainingTime = 0;
        return $scope.$apply();
      };
      if (FSScanService.getScannerState() === FSEnum.states.CALIBRATING) {
        $scope.showStream = true;
      }
      $scope.$on(FSEnum.events.ON_STATE_CHANGED,
    function(event,
    data) {
        // if data['state'] == FSEnum.states.SETTINGS
        //    startStream()
        if (data['state'] === FSEnum.states.IDLE) {
          return stopStream();
        }
      });
      $rootScope.$on('clearView',
    function() {
        return $scope.clearView();
      });
      $scope.start_stream_conditions = ['SCANNING_TEXTURE',
    'START_CALIBRATION'];
      $scope.stop_stream_conditions = ['STOP_CALIBRATION',
    'SCANNING_OBJECT'];
      $scope.reset_conditions = ['SCAN_CANCELED',
    'SCAN_STOPED'];
      $scope.$on(FSEnum.events.ON_INFO_MESSAGE,
    function(event,
    data) {
        var ref,
    ref1,
    ref2;
        if (ref = data['message'],
    indexOf.call($scope.start_stream_conditions,
    ref) >= 0) {
          startStream();
        }
        if (ref1 = data['message'],
    indexOf.call($scope.stop_stream_conditions,
    ref1) >= 0) {
          stopStream();
        }
        if (ref2 = data['message'],
    indexOf.call($scope.reset_conditions,
    ref2) >= 0) {
          resetSate();
        }
        if (data['message'] === 'SCAN_COMPLETE') {
          stopStream();
          FSScanService.setScanId(data['scan_id']);
          $scope.setScanIsComplete(true);
          return resetSate();
        }
      });
      $scope.$on(FSEnum.events.ON_NEW_PROGRESS,
    function(event,
    data) {
        var _time_values,
    percentage,
    timeTaken;
        if (FSScanService.state !== FSEnum.states.IDLE) {
          $scope.resolution = data['resolution'];
          $scope.progress = data['progress'];
          percentage = $scope.progress / $scope.resolution * 100;
          $scope.startTime = data['starttime'];
          if ($scope.progress <= 1) {
            $scope.sampledRemainingTime = 0;
            _time_values = [];
          } else {
            //ngProgress.start()
            timeTaken = data['timestamp'] - $scope.startTime;
            $scope.remainingTime.push(parseFloat(Math.floor(((timeTaken / $scope.progress) * ($scope.resolution - $scope.progress)) / 1000)));
            if ($scope.remainingTime.length > 20) {
              _time_values = $scope.remainingTime.slice(Math.max($scope.remainingTime.length - 8,
    1));
            } else {
              _time_values = $scope.remainingTime;
            }
            $scope.sampledRemainingTime = parseFloat(Math.floor(median(_time_values)));
            if ($scope.sampledRemainingTime >= 60) {
              $scope.remainingTimeString = parseInt($scope.sampledRemainingTime / 60) + " minutes";
            } else {
              $scope.remainingTimeString = $scope.sampledRemainingTime + " seconds";
            }
            $log.debug(percentage.toFixed(2) + "% complete");
            ngProgress.set(percentage);
          }
          if (percentage >= 98) {
            $scope.sampledRemainingTime = 0;
            _time_values = [];
          }
          return $scope.addPoints(data['points'],
    data['progress'],
    data['resolution']);
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
        values.sort(function(a,
    b) {
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
    '$log',
    '$scope',
    '$rootScope',
    'ngProgress',
    '$http',
    'common.services.Configuration',
    'fabscan.services.FSEnumService',
    'fabscan.services.FSScanService',
    'fabscan.services.FSMessageHandlerService',
    function($log,
    $scope,
    $rootScope,
    ngProgress,
    $http,
    Configuration,
    FSEnumService,
    FSScanService,
    FSMessageHandlerService) {
      $scope.showSettings = false;
      $scope.scanListLoaded = false;
      $scope.loadDialog = false;
      $scope.shareDialog = false;
      $scope.configDialog = false;
      $scope.createScreenShot = null;
      $scope.scans = [];
      $scope.m_filters = [];
      $scope.loadFilters = function() {
        var filter_promise;
        filter_promise = $http.get(Configuration.installation.apiurl + 'api/v1/filters/');
        return filter_promise.then(function(payload) {
          $log.info(payload);
          $scope.m_filters = payload.data.filters;
          $scope.m_filters.sort(function(a,
    b) {
            var x,
    y;
            x = a.file_name.toLowerCase();
            y = b.file_name.toLowerCase();
            if (x < y) {
              return -1;
            } else if (x > y) {
              return 1;
            } else {
              return 0;
            }
          });
          return $scope.selectedFilter = $scope.m_filters[0]['file_name'];
        });
      };
      $scope.loadFilters();
      $scope.restartServer = function() {
        return FSScanService.restartServer();
      };
      $scope.startCalibration = function() {
        return FSScanService.startCalibration();
      };
      $scope.startScan = function() {
        $scope.stopStream();
        $scope.remainingTime = [];
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
      $scope.showConfigDialog = function() {
        $log.debug("Open Config Dialog");
        return $scope.configDialog = true;
      };
      $scope.hideConfigDialog = function() {
        return $scope.configDialog = false;
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
        $scope.displayNews(false);
        if (!$scope.loadDialog) {
          promise = $http.get(Configuration.installation.apiurl + 'api/v1/scans/');
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
        //window.stop()
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
    '$log',
    '$scope',
    '$timeout',
    '$swipe',
    '$http',
    'common.services.Configuration',
    'fabscan.services.FSEnumService',
    'fabscan.services.FSMessageHandlerService',
    'fabscan.services.FSScanService',
    function($log,
    $scope,
    $timeout,
    $swipe,
    $http,
    Configuration,
    FSEnumService,
    FSMessageHandlerService,
    FSScanService) {
      var devices_promise,
    updateSettings;
      //if FSScanService.getScannerState() == FSEnumService.states.UPDATING_SETTINGS
      $scope.streamUrl = Configuration.installation.apiurl + 'api/v1/streams/?type=laser';
      $scope.previewMode = "laser";
      $scope.selectedTab = 'general';
      devices_promise = $http.get(Configuration.installation.httpurl + 'api/v1/devices/');
      devices_promise.then(function(payload) {
        $log.info(payload);
        return $scope.devices = payload.data;
      });
      //$scope.logResize = ()->
      //  element = angular.element(document.querySelector('#settingsWindow'));
      //  height = element[0].offsetHeight;
      //  width = element[0].offsetWidth;
      //  console.log(width)
      //  #height = window.innerHeight
      //  document.getElementById('settings-preview').setAttribute("style","height:" + height + "px");
      //  #console.log(height)
      $scope.sendDeviceCommand = function(device,
    f_name) {
        var message;
        message = {};
        message = {
          event: FSEnumService.events.COMMAND,
          data: {
            command: FSEnumService.commands.HARDWARE_TEST_FUNCTION,
            device: {
              name: device,
              function: f_name
            }
          }
        };
        return FSMessageHandlerService.sendData(message);
      };
      $scope.timeout = null;
      updateSettings = function() {
        var _settings;
        _settings = {};
        angular.copy($scope.settings,
    _settings);
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
        $scope.streamUrl = Configuration.installation.apiurl + 'api/v1/streams/?type=texture';
        return $scope.previewMode = "calibration";
      };
      //$scope.$apply()
      $scope.showLaserPreview = function() {
        $scope.streamUrl = Configuration.installation.apiurl + 'api/v1/streams/?type=laser';
        return $scope.previewMode = "laser";
      };
      //$scope.$apply()
      $scope.calibrationPatternSelected = function() {
        if ($scope.settings.show_calibration_pattern) {
          return true;
        } else {
          return false;
        }
      };
      $scope.laserOverlaySelected = function() {
        if ($scope.settings.show_laser_overlay) {
          return true;
        } else {
          return false;
        }
      };
      $scope.setCalibrationPattern = function() {
        return updateSettings();
      };
      $scope.setLaserOverlay = function() {
        return updateSettings();
      };
      $scope.setColor = function() {
        return updateSettings();
      };
      $scope.setAutoThreshold = function() {
        return updateSettings();
      };
      $scope.autoThreshHoldIsSelected = function() {
        if ($scope.settings.auto_threshold) {
          return true;
        } else {
          return false;
        }
      };
      $scope.colorIsSelected = function() {
        if ($scope.settings.color) {
          return true;
        } else {
          return false;
        }
      };
      $scope.$watch('settings.resolution',
    function(newVal,
    oldVal) {
        if (newVal !== oldVal) {
          updateSettings();
          $timeout.cancel($scope.timeout);
          $scope.showResolutionValue = true;
          return $scope.timeout = $timeout((function() {
            $scope.showResolutionValue = false;
          }),
    600);
        }
      },
    true);
      $scope.$watch('settings.laser_positions',
    function(newVal,
    oldVal) {
        if (newVal !== oldVal) {
          updateSettings();
          $timeout.cancel($scope.timeout);
          $scope.showPositionValue = true;
          return $scope.timeout = $timeout((function() {
            $scope.showPositionValue = false;
          }),
    600);
        }
      },
    true);
      $scope.$watch('settings.threshold',
    function(newVal,
    oldVal) {
        if (newVal !== oldVal) {
          updateSettings();
          $timeout.cancel($scope.timeout);
          $scope.showThresholdValue = true;
          return $scope.timeout = $timeout((function() {
            $scope.showThresholdValue = false;
          }),
    200);
        }
      },
    true);
      $scope.$watch('settings.camera.saturation',
    function(newVal,
    oldVal) {
        if (newVal !== oldVal) {
          updateSettings();
          $timeout.cancel($scope.timeout);
          $scope.showSaturationValue = true;
          return $scope.timeout = $timeout((function() {
            $scope.showSaturationValue = false;
          }),
    200);
        }
      },
    true);
      $scope.$watch('settings.camera.contrast',
    function(newVal,
    oldVal) {
        if (newVal !== oldVal) {
          updateSettings();
          $timeout.cancel($scope.timeout);
          $scope.showContrastValue = true;
          return $scope.timeout = $timeout((function() {
            $scope.showContrastValue = false;
          }),
    200);
        }
      },
    true);
      $scope.$watch('settings.camera.brightness',
    function(newVal,
    oldVal) {
        if (newVal !== oldVal) {
          updateSettings();
          $timeout.cancel($scope.timeout);
          $scope.showBrightnessValue = true;
          return $scope.timeout = $timeout((function() {
            $scope.showBrightnessValue = false;
          }),
    200);
        }
      },
    true);
      $scope.$watch('settings.led.red',
    function(newVal,
    oldVal) {
        if (newVal !== oldVal) {
          updateSettings();
          $timeout.cancel($scope.timeout);
          $scope.showLedRedValue = true;
          return $scope.timeout = $timeout((function() {
            $scope.showLedRedValue = false;
          }),
    200);
        }
      },
    true);
      $scope.$watch('settings.led.green',
    function(newVal,
    oldVal) {
        if (newVal !== oldVal) {
          updateSettings();
          $timeout.cancel($scope.timeout);
          $scope.showLedGreenValue = true;
          return $scope.timeout = $timeout((function() {
            $scope.showLedGreenValue = false;
          }),
    200);
        }
      },
    true);
      return $scope.$watch('settings.led.blue',
    function(newVal,
    oldVal) {
        if (newVal !== oldVal) {
          updateSettings();
          $timeout.cancel($scope.timeout);
          $scope.showLedBlueValue = true;
          return $scope.timeout = $timeout((function() {
            $scope.showLedBlueValue = false;
          }),
    200);
        }
      },
    true);
    }
  ]);

}).call(this);

(function() {
  var name;

  name = "fabscan.controller.FSShareController";

  angular.module(name, []).controller(name, [
    '$log',
    '$scope',
    '$rootScope',
    '$http',
    'common.services.toastrWrapperSvc',
    'common.services.Configuration',
    'fabscan.services.FSScanService',
    function($log,
    $scope,
    $rootScope,
    $http,
    toaster,
    Configuration,
    FSScanService) {
      var getFileExtension;
      $scope.settings = null;
      $scope.id = FSScanService.getScanId();
      $scope.selectedTab = 'download';
      $scope.selectedFile = null;
      $scope.raw_scans = [];
      $scope.meshes = [];
      // used for debugging...
      //$scope.raw_scans = [{type:'ply',name:'raw_scan_0.ply',file_name:'raw_scan_0.ply',url:'http://irgendwas'},{type:'ply',name:'raw_scan_0.ply',file_name:'raw_scan_0.ply',url:'http://irgendwas'},{type:'ply',name:'raw_scan_0.ply',filter_name:'raw_scan_0',url:'http://irgendwas'},{type:'ply',name:'raw_scan_0.ply',filter_name:'raw_scan_0.ply',url:'http://irgendwas'},{type:'ply',name:'raw_scan_0.ply',filter_name:'raw_scan_0.ply',url:'http://irgendwas'}]
      //$scope.meshes = [{type:'ply',name:'raw_scan_0.ply',filter_name:'raw_scan_0',url:'http://irgendwas'},{type:'ply',name:'raw_scan_0.ply',filter_name:'raw_scan_0',url:'http://irgendwas'},{type:'ply',name:'raw_scan_0.ply',filter_name:'raw_scan_0',url:'http://irgendwas'},{type:'ply',name:'raw_scan_0.ply',filter_name:'raw_scan_0',url:'http://irgendwas'},{type:'ply',name:'raw_scan_0.ply',filter_name:'raw_scan_0',url:'http://irgendwas'}]
      //$scope.m_filters = [{file_name:'filter_1.mlx',name:'filter_1'},{file_name:'filter_2.mlx',name:'filter_2'},{file_name:'filter_3.mlx',name:'filter_3'}]
      $scope.file_formats = ['ply',
    'stl',
    'obj',
    'off',
    'xyz',
    'x3d',
    '3ds'];
      $scope.selectedFormat = $scope.file_formats[0];
      $scope.getScans = function() {
        var scan_promise;
        scan_promise = $http.get(Configuration.installation.apiurl + 'api/v1/scans/' + FSScanService.getScanId());
        return scan_promise.then(function(payload) {
          $log.debug(payload);
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
          afterChange: function(event,
    slick,
    currentSlide,
    nextSlide) {
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
          afterChange: function(event,
    slick,
    currentSlide,
    nextSlide) {
            return $scope.selectedFilter = $(slick.$slides.get(currentSlide)).data('value');
          }
        }
      };
      $scope.appendFormatListener = function() {
        $('.f_format').on('afterChange',
    function(event,
    slick,
    currentSlide,
    nextSlide) {
          return $scope.selectedFormat = $(slick.$slides.get(currentSlide)).data('value');
        });
      };
      $scope.appendFilterListener = function() {
        $('.m_filter').on('afterChange',
    function(event,
    slick,
    currentSlide,
    nextSlide) {
          return $scope.selectedFilter = $(slick.$slides.get(currentSlide)).data('value');
        });
      };
      $scope.selectTab = function(tab) {
        return $scope.selectedTab = tab;
      };
      $scope.nextSubSelection = function(id) {
        $scope.selectedFile = id;
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
        promise = $http.delete(Configuration.installation.apiurl + 'api/v1/scans/' + FSScanService.getScanId() + '/files?filename=' + filename);
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
            else: toaster.info('File "' + filename + '" deleted')
          };
        });
      };
      $scope.deleteScan = function() {
        var promise;
        $scope.toggleShareDialog();
        promise = $http.delete(Configuration.installation.apiurl + 'api/v1/scans/' + FSScanService.getScanId());
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
      return $scope.runMeshing = function(file) {
        $scope.toggleShareDialog();
        $log.info($scope.selectedFilter);
        $log.info($scope.selectedFormat);
        return FSScanService.runMeshing(FSScanService.getScanId(),
    $scope.selectedFilter,
    $scope.selectedFormat,
    $scope.selectedFile);
      };
    }
  ]);

}).call(this);

(function() {
  var name;

  name = "fabscan.controller.FSStartupController";

  angular.module(name, []).controller(name, ['$log', '$scope', '$rootScope', 'fabscan.services.FSEnumService', 'fabscan.services.FSScanService', 'fabscan.services.FSMessageHandlerService', function($log, $scope, $rootScope, FSEnumService, FSScanService, FSMessageHandlerService) {}]);

}).call(this);
