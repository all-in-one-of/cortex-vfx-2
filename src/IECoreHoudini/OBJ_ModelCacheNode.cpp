//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2013, Image Engine Design Inc. All rights reserved.
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

#include "OBJ/OBJ_Geometry.h"
#include "OBJ/OBJ_SubNet.h"

#include "IECoreHoudini/Convert.h"
#include "IECoreHoudini/OBJ_ModelCacheNode.h"

using namespace IECore;
using namespace IECoreHoudini;

template<typename BaseType>
OBJ_ModelCacheNode<BaseType>::OBJ_ModelCacheNode( OP_Network *net, const char *name, OP_Operator *op ) : ModelCacheNode<BaseType>( net, name, op )
{
}

template<typename BaseType>
OBJ_ModelCacheNode<BaseType>::~OBJ_ModelCacheNode()
{
}

template<typename BaseType>
PRM_Name OBJ_ModelCacheNode<BaseType>::pBuild( "build", "Build" );

static void copyAndHideParm( PRM_Template &src, PRM_Template &dest )
{
	PRM_Name *name = new PRM_Name( src.getToken(), src.getLabel(), src.getExpressionFlag() );
	name->harden();
	
	dest.initialize(
		(PRM_Type) (src.getType() | PRM_TYPE_INVISIBLE),
		src.getTypeExtended(),
		src.exportLevel(),
		src.getVectorSize(),
		name,
		src.getFactoryDefaults(),
		src.getChoiceListPtr(),
		src.getRangePtr(),
		src.getCallback(),
		src.getSparePtr(),
		src.getParmGroup(),
		(const char *)src.getHelpText(),
		src.getConditionalBasePtr()
	);
}

template<typename BaseType>
OP_TemplatePair *OBJ_ModelCacheNode<BaseType>::buildParameters()
{
	static PRM_Template *thisTemplate = 0;
	if ( !thisTemplate )
	{
		PRM_Template *objTemplate = BaseType::getTemplateList( OBJ_PARMS_PLAIN );
		unsigned numObjParms = PRM_Template::countTemplates( objTemplate );
		unsigned numMDCParms = PRM_Template::countTemplates( ModelCacheNode<BaseType>::parameters );
		thisTemplate = new PRM_Template[ numObjParms + numMDCParms + 2 ];
		
		for ( unsigned i = 0; i < numObjParms; ++i )
		{
			thisTemplate[i] = objTemplate[i];
			copyAndHideParm( objTemplate[i], thisTemplate[i] );
		}
		
		for ( unsigned i = 0; i < numMDCParms; ++i )
		{
			thisTemplate[numObjParms+i] = ModelCacheNode<BaseType>::parameters[i];
		}
		
		thisTemplate[numObjParms + numMDCParms] = PRM_Template(
			PRM_CALLBACK, 1, &pBuild, 0, 0, 0, &OBJ_ModelCacheNode<BaseType>::buildButtonCallback, 0, 0,
			"Build the hierarchy below the specified root path.\n"
			"Some nodes may define additional options that are used during the build process."
		);
	}
	
	static OP_TemplatePair *templatePair = 0;
	if ( !templatePair )
	{
		templatePair = new OP_TemplatePair( thisTemplate );
	}
	
	return templatePair;
}

template<typename BaseType>
int OBJ_ModelCacheNode<BaseType>::buildButtonCallback( void *data, int index, float time, const PRM_Template *tplate )
{
	std::string file;
	OBJ_ModelCacheNode<BaseType> *node = reinterpret_cast<OBJ_ModelCacheNode<BaseType>*>( data );
	if ( !node || !node->ensureFile( file ) )
	{
		return 0;
	}
	
	return 1;
}

template<typename BaseType>
OP_ERROR OBJ_ModelCacheNode<BaseType>::cookMyObj( OP_Context &context )
{
	std::string file;
	if ( !ModelCacheNode<BaseType>::ensureFile( file ) )
	{
		ModelCacheNode<BaseType>::addError( OBJ_ERR_CANT_FIND_OBJ, ( file + " is not a valid .mdc" ).c_str() );
		return ModelCacheNode<BaseType>::error();
	}
	
	std::string path = ModelCacheNode<BaseType>::getPath();
	ModelCacheNode<OP_Node>::Space space = (ModelCacheNode<OP_Node>::Space)evalInt( ModelCacheNode<BaseType>::pSpace.getToken(), 0, 0 );
	
	Imath::M44d transform;
	if ( space == ModelCacheNode<OP_Node>::World )
	{
		transform = ModelCacheNode<BaseType>::cache().worldTransform( file, path );
	}
	else if ( space == ModelCacheNode<OP_Node>::Leaf )
	{
		transform = ModelCacheNode<BaseType>::cache().entry( file, path )->modelCache()->readTransform();
	}
	
	ModelCacheNode<BaseType>::setParmTransform( context, IECore::convert<UT_Matrix4D>( transform ) );
	
	return BaseType::cookMyObj( context );
}

//////////////////////////////////////////////////////////////////////////////////////////
// Known Specializations
//////////////////////////////////////////////////////////////////////////////////////////

template class OBJ_ModelCacheNode<OBJ_Geometry>;
template class OBJ_ModelCacheNode<OBJ_SubNet>;
