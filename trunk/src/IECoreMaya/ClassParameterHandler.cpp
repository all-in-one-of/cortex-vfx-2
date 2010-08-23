//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2010, Image Engine Design Inc. All rights reserved.
//
//  Redistribution and use in source and binary forms, with or without
//  modification, are permitted provided that the following conditions are
//  met:
//
//     * Redistributions of source code must retain the above copyright
//       notice, this list of conditions and the following disclaimer.
//
//     * Redistributions in binary form must reproduce the above copyright
//       notice, this list of conditions and the following disclaimer in the
//       documentation and/or other materials provided with the distribution.
//
//     * Neither the name of Image Engine Design nor the names of any
//       other contributors to this software may be used to endorse or
//       promote products derived from this software without specific prior
//       written permission.
//
//  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
//  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
//  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
//  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
//  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
//  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
//  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
//  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
//  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
//  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
//  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//
//////////////////////////////////////////////////////////////////////////

#include "boost/python.hpp"

#include "maya/MFnCompoundAttribute.h"
#include "maya/MFnNumericAttribute.h"
#include "maya/MFnTypedAttribute.h"
#include "maya/MGlobal.h"

#include "IECorePython/ScopedGILLock.h"

#include "IECoreMaya/ClassParameterHandler.h"

using namespace IECoreMaya;
using namespace boost::python;

static ParameterHandler::Description<ClassParameterHandler> registrar( IECore::ClassParameterTypeId );

MStatus ClassParameterHandler::setClass( IECore::ParameterPtr parameter, const MString &className, int classVersion, const MString &searchPathEnvVar )
{	
	IECorePython::ScopedGILLock gilLock;
	try
	{
		boost::python::object pythonParameter( parameter );
		pythonParameter.attr( "setClass" )( className.asChar(), classVersion, searchPathEnvVar.asChar() );
	}
	catch( boost::python::error_already_set )
	{
		PyErr_Print();
		return MS::kFailure;
	}
	catch( const std::exception &e )
	{
		MGlobal::displayError( MString( "ClassParameterHandler::setClass : " ) + e.what() );
		return MS::kFailure;
	}
	return MS::kSuccess;
}

MStatus ClassParameterHandler::getClass( IECore::ConstParameterPtr parameter, MString &className, int &classVersion, MString &searchPathEnvVar )
{
	IECorePython::ScopedGILLock gilLock;
	try
	{
		boost::python::object pythonParameter( IECore::constPointerCast<IECore::Parameter>( parameter ) );
		boost::python::tuple classInfo = extract<tuple>( pythonParameter.attr( "getClass" )( true ) );
		
		className = extract<const char *>( classInfo[1] );
		classVersion = extract<int>( classInfo[2] );
		searchPathEnvVar = extract<const char *>( classInfo[3] );
		
		return MS::kSuccess;
	}
	catch( boost::python::error_already_set )
	{
		PyErr_Print();
	}
	catch( const std::exception &e )
	{
		MGlobal::displayError( MString( "ClassParameterHandler::getClass : " ) + e.what() );
	}
	return MS::kFailure;
}

void ClassParameterHandler::currentClass( const MPlug &plug, MString &className, int &classVersion, MString &searchPathEnvVar )
{
	className = plug.child( 0 ).asString();
	classVersion = plug.child( 1 ).asInt();
	searchPathEnvVar = plug.child( 2 ).asString();
}

MStatus ClassParameterHandler::doRestore( const MPlug &plug, IECore::ParameterPtr parameter )
{
	MString className;
	int classVersion;
	MString searchPathEnvVar;
	currentClass( plug, className, classVersion, searchPathEnvVar );
	return setClass( parameter, className, classVersion, searchPathEnvVar );
}
				
MStatus ClassParameterHandler::doUpdate( IECore::ConstParameterPtr parameter, MPlug &plug ) const
{
	if( !parameter || !parameter->isInstanceOf( IECore::ClassParameterTypeId ) )
	{
		return MS::kFailure;
	}

	MObject attribute = plug.attribute();
	MFnCompoundAttribute fnCAttr( attribute );
	if( !fnCAttr.hasObj( attribute ) )
	{
		return MS::kFailure;
	}

	if( fnCAttr.numChildren()!=3 )
	{
		return MS::kFailure;
	}

	MObject classNameAttr = fnCAttr.child( 0 );
	MFnTypedAttribute fnTAttr( classNameAttr );
	if( !fnTAttr.hasObj( classNameAttr ) )
	{
		return MS::kFailure;	
	}
	if( fnTAttr.name() != fnCAttr.name() + "__className" )
	{
		return MS::kFailure;
	}
	if( fnTAttr.attrType()!=MFnData::kString )
	{
		return MS::kFailure;
	}
	
	MObject classVersionAttr = fnCAttr.child( 1 );
	MFnNumericAttribute fnNAttr( classVersionAttr );
	if( !fnNAttr.hasObj( classVersionAttr ) )
	{
		return MS::kFailure;
	}
	if( fnNAttr.name() != fnCAttr.name() + "__classVersion" )
	{
		return MS::kFailure;
	}
	if( fnNAttr.unitType() != MFnNumericData::kInt )
	{
		return MS::kFailure;
	}
	
	MObject searchPathEnvVarAttr = fnCAttr.child( 2 );
	fnTAttr.setObject( searchPathEnvVarAttr );
	if( !fnTAttr.hasObj( searchPathEnvVarAttr ) )
	{
		return MS::kFailure;	
	}
	if( fnTAttr.name() != fnCAttr.name() + "__searchPathEnvVar" )
	{
		return MS::kFailure;
	}
	if( fnTAttr.attrType()!=MFnData::kString )
	{
		return MS::kFailure;
	}

	if( !storeClass( parameter, plug ) )
	{
		return MS::kFailure;
	}
	
	return finishUpdating( parameter, plug );
}

MPlug ClassParameterHandler::doCreate( IECore::ConstParameterPtr parameter, const MString &plugName, MObject &node ) const
{	
	if( !parameter || !parameter->isInstanceOf( IECore::ClassParameterTypeId ) )
	{
		return MPlug();
	}

	MFnCompoundAttribute fnCAttr;
	MObject attribute = fnCAttr.create( plugName, plugName );
	
	MFnTypedAttribute fnTAttr;
	MObject classNameAttr = fnTAttr.create( plugName + "__className", plugName + "__className", MFnData::kString );
	fnCAttr.addChild( classNameAttr );
	
	MFnNumericAttribute fnNAttr;
	MObject classVersionAttr = fnNAttr.create( plugName + "__classVersion", plugName + "__classVersion", MFnNumericData::kInt );
	fnCAttr.addChild( classVersionAttr );
	
	MObject searchPathEnvVarAttr = fnTAttr.create( plugName + "__searchPathEnvVar", plugName + "__searchPathEnvVar", MFnData::kString );
	fnCAttr.addChild( searchPathEnvVarAttr );
	
	MPlug result = finishCreating( parameter, attribute, node );
	
	if( !storeClass( parameter, result ) )
	{
		return MPlug(); // failure
	}
	
	if( !finishUpdating( parameter, result ) )
	{
		return MPlug(); // failure
	}
	
	return result;
}

MStatus ClassParameterHandler::doSetValue( IECore::ConstParameterPtr parameter, MPlug &plug ) const
{
	if( !parameter || !parameter->isInstanceOf( IECore::ClassParameterTypeId ) )
	{
		return MS::kFailure;
	}
	return MS::kSuccess;
}

MStatus ClassParameterHandler::doSetValue( const MPlug &plug, IECore::ParameterPtr parameter ) const
{
	if( !parameter || !parameter->isInstanceOf( IECore::ClassParameterTypeId ) )
	{
		return MS::kFailure;
	}
	
	return MS::kSuccess;
}

MStatus ClassParameterHandler::storeClass( IECore::ConstParameterPtr parameter, MPlug &plug )
{
	IECorePython::ScopedGILLock gilLock;
	try
	{
		boost::python::object pythonParameter( IECore::constPointerCast<IECore::Parameter>( parameter ) );
		boost::python::object classInfo = pythonParameter.attr( "getClass" )( true );
	
		std::string className = boost::python::extract<std::string>( classInfo[1] );
		int classVersion = boost::python::extract<int>( classInfo[2] );
		std::string searchPathEnvVar = boost::python::extract<std::string>( classInfo[3] );
	
		// only set the plug values if the new value is genuinely different, as otherwise
		// we end up generating unwanted reference edits.
		MPlug classNamePlug = plug.child( 0 );
		MString storedClassName = classNamePlug.asString();
		if( storedClassName != className.c_str() )
		{
			classNamePlug.setString( className.c_str() );
		}
		
		MPlug classVersionPlug = plug.child( 1 );
		int storedClassVersion = classVersionPlug.asInt();
		if( storedClassVersion != classVersion )
		{
			classVersionPlug.setInt( classVersion );
		}
		
		MPlug searchPathEnvVarPlug = plug.child( 2 );
		MString storedSearchPathEnvVar = searchPathEnvVarPlug.asString();
		if( storedSearchPathEnvVar != searchPathEnvVar.c_str() )
		{
			searchPathEnvVarPlug.setString( searchPathEnvVar.c_str() );
		}
	}
	catch( boost::python::error_already_set )
	{
		PyErr_Print();
		return MS::kFailure;
	}
	catch( const std::exception &e )
	{
		MGlobal::displayError( MString( "ClassParameterHandler::setClass : " ) + e.what() );
		return MS::kFailure;
	}
	
	return MS::kSuccess;
}
