cmake_minimum_required(VERSION 3.11 FATAL_ERROR)
project(cmake-fetchcontent)
set(CMAKE_CXX_STANDARD 11)
set(HEADER_FILES glicko2.h)

include(FetchContent)
FetchContent_Declare(
  rapidcsv
  GIT_REPOSITORY "https://github.com/d99kris/rapidcsv.git"
  GIT_TAG        "v8.50"
)
FetchContent_MakeAvailable(rapidcsv)

add_executable(cfb cfb.cpp)
target_link_libraries(cfb PUBLIC rapidcsv)
install(TARGETS cfb DESTINATION bin)

add_custom_target(uninstall
  COMMAND "${CMAKE_COMMAND}" -E remove "${CMAKE_INSTALL_PREFIX}/bin/cfb"
)
