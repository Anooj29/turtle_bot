cmake_minimum_required(VERSION 3.8)
project(turtle_bot)

find_package(ament_cmake REQUIRED)

install(DIRECTORY
  urdf
  launch
  worlds
  config
  rviz
  maps
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/teleop_arrow_keys.py
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
