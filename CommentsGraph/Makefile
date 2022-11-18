CC:= cl.exe
LL:= lld-link
CXXFLAGS:= /O2
INCLUDES:= -I ${BOOST_ROOT} -I ./include
LINK_OPTS:= /LIBPATH:"$(BOOST_LIB)"

#"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"

ifndef BOOST_ROOT
$(error Boost directory is not specified. Declare BOOST_ROOT variable.)
endif

ifndef BOOST_LIB
$(error Boost directory is not specified. Declare BOOST_LIB variable.)
endif

.PHONY : clean

clean:
	@del *.obj
	@del *.exe

all: enumerate_channel_ids enumerate_comments comment_channel_aggregation

enumerate_channel_ids:
	$(CC) enumerate_channel_ids.cxx $(INCLUDES) $(CXXFLAGS) /link $(LINK_OPTS)

enumerate_comments:
	$(CC) enumerate_comments.cxx $(INCLUDES) $(CXXFLAGS) /link $(LINK_OPTS)

comment_channel_aggregation:
	$(CC) comment_channel_aggregation.cxx $(INCLUDES) $(CXXFLAGS) /link $(LINK_OPTS)