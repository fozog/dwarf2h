#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

struct _CSConfigCallerSignature;

typedef uint64_t CT_uint64_t;

typedef CT_uint64_t CoreTrustPolicyFlags;

typedef CoreTrustPolicyFlags CMSPolicyFlags_t;

struct _CSConfigFeatureSet {
    _Bool restrictedExecutionMode;
    _Bool OOPJit;
    _Bool localSigning;
    _Bool compilationService;
    _Bool appleInternalProfiles;
    _Bool developerMode;
    _Bool demoMode;
    _Bool JIT;
    _Bool executableCommPage;
};
typedef struct _CSConfigFeatureSet CSConfigFeatureSet_t;

struct _CSConfigOSPolicy {
    uint32_t minimumCodeDirectoryVersion;
    uint8_t minimumHashTypeForPlatformCode;
    _Bool trustCacheCodeOnly;
    _Bool platformCodeOnly;
    CMSPolicyFlags_t platformCTFlags;
    CMSPolicyFlags_t appStoreCTFlags;
    CMSPolicyFlags_t profileValidatedCTFlags;
    CMSPolicyFlags_t appStoreQACTFlags;
    CMSPolicyFlags_t profileValidatedQACTFlags;
    CMSPolicyFlags_t profileCTFlags;
    const char** developerLimit;
    CSConfigFeatureSet_t featureSet;
    struct  {
        const char* appContainerPath;
    } specialPaths;
};

typedef struct _CSConfigOSPolicy CSConfigOSPolicy_t;
typedef void* (*CERuntimeMalloc)(size_t);

typedef void (*CERuntimeFree)(void*);

typedef void (*CERuntimeLog)(const char*);

typedef void (*CERuntimeAbort)(const char*);

typedef const struct CERuntime* CERuntime_t;

typedef _Bool (*CERuntimeInternalStatus)(const CERuntime_t);

typedef void* (*CERuntimeAllocIndex)(size_t);

typedef void (*CERuntimeFreeIndex)(size_t);
struct CERuntime {
    const uint64_t version;
    const CERuntimeMalloc alloc;
    const CERuntimeFree free;
    const CERuntimeLog log;
    const CERuntimeAbort abort;
    const CERuntimeInternalStatus internalStatus;
    const CERuntimeAllocIndex allocIndex;
    const CERuntimeFreeIndex freeIndex;
};

typedef struct CERuntime EntitlementsRuntime_t;

typedef uint8_t TCType_t;

struct _TrustCacheModuleBase {
    uint32_t version;
};
typedef struct _TrustCacheModuleBase TrustCacheModuleBase_t;

struct _TrustCache {
    _Atomic(struct _TrustCache*) next;
    TCType_t type;
    _Bool tombstoned;
    size_t moduleSize;
    const TrustCacheModuleBase_t* module;
};
typedef struct _TrustCache TrustCache_t;

struct _TrustCacheQueryToken {
    const TrustCache_t* trustCache;
    void* trustCacheEntry;
};

typedef enum  {
    kCSRestrictedModePermNever = 0,
    kCSRestrictedModePermBefore = 1,
    kCSRestrictedModePermAfter = 2,
    kCSRestrictedModePermBoth = 3,
} CSRestrictedModePerms_t;
typedef enum  {
    kCEContextTypeEntitlements = 0,
    kCEContextTypeProvisioningProfileEntitlements = 1,
    kCEContextTypeProvisioningProfile = 2,
    kCEContextTypeLWCR = 3,
    kCEContextTypeTotal = 4,
} CEContextType_t;
typedef uint32_t CEFormatVersion_t;
typedef struct _TCReturn TCReturn_t;
struct _CEContextInfo {
    CEContextType_t type;
    CEFormatVersion_t version;
};
struct CEAccelerationElement {
    uint32_t key_offset;
    uint32_t key_length;
};
typedef struct CEAccelerationElement CEAccelerationElement_t;

struct CEAccelerationContext {
    CEAccelerationElement_t* index;
    size_t index_count;
};
struct ccder_read_blob {
    const uint8_t* der;
    const uint8_t* der_end;
};
typedef struct ccder_read_blob ccder_read_blob;
typedef unsigned long ccder_tag;
typedef struct _CEContextInfo CEContextInfo_t;
struct der_vm_context {
    CERuntime_t runtime;
    struct CEAccelerationContext lookup;
    ccder_tag dictionary_tag;
    _Bool sorted;
    _Bool valid;
    union  {
        ccder_read_blob ccstate;
        struct  {
            const uint8_t* der_start;
            const uint8_t* der_end;
        } state;
    };
};

struct _CSBuffer {
    const uint8_t* data;
    size_t dataSize;
};
typedef struct _CSBuffer CSBuffer_t;


typedef struct der_vm_context der_vm_context_t;
struct CEQueryContext {
    der_vm_context_t der_context;
    _Bool managed;
};
struct _CEContext {
    CEContextInfo_t info;
    struct CEQueryContext legacyContext;
};
typedef struct _CEContext CEContext_t;

typedef CEContext_t EntitlementsContext_t;
typedef struct _TrustCacheQueryToken TrustCacheQueryToken_t;
struct _CSConfigTrustCaches {
    TCReturn_t (*queryCDHash)(TrustCacheQueryToken_t*);
    TCReturn_t (*queryCDHashForREM)(CSRestrictedModePerms_t*);
    _Bool queryTokenSupported;
};
typedef struct _CSConfigTrustCaches CSConfigTrustCaches_t;
struct _CSConfigProvisioningProfiles {
    char deviceUDID[32];
    _Bool (*auxiliaryValidate)(void*);
};
struct _CSConfigLocalSigning {
    CSBuffer_t (*getPublicKey)(void);
    _Bool (*matchAuthentication)(const uint8_t*);
    EntitlementsContext_t* allowedEntitlementsSet;
};
typedef struct _CSConfigLocalSigning CSConfigLocalSigning_t;
typedef struct _CSConfigProvisioningProfiles CSConfigProvisioningProfiles_t;

struct _CSConfigCompilationService {
    _Bool (*matchCDHash)(const uint8_t*);
};
typedef struct _CSConfigCompilationService CSConfigCompilationService_t;


typedef struct _SignatureValidation SignatureValidation_t;

struct _CSConfigCallerSignature {
    const SignatureValidation_t* (*acquireSig)(void**);
    void (*releaseSig)(void*);
};

typedef struct _CSConfigCallerSignature CSConfigCallerSignature_t;

struct _CSConfigEnvironmentState {
    _Bool (*developerMode)(void);
    _Bool (*demoMode)(void);
    _Bool (*lockdownMode)(void);
    _Bool (*researchMode)(void);
    _Bool (*extendedResearchMode)(void);
};

typedef struct _CSConfigEnvironmentState CSConfigEnvironmentState_t;
typedef struct _CSMutableBuffer CSMutableBuffer_t;

struct _CSConfig {
    const CSConfigOSPolicy_t* systemPolicy;
    _Bool (*platformCodeOnly)(void);
    const EntitlementsRuntime_t* entitlementsRuntime;
    CSConfigTrustCaches_t trustCaches;
    CSConfigProvisioningProfiles_t provisioningProfiles;
    CSConfigLocalSigning_t localSigning;
    CSConfigCompilationService_t compilationService;
    CSConfigCallerSignature_t callerSignature;
    CSConfigEnvironmentState_t environmentState;
    CSMutableBuffer_t (*getMutableBuffer)(CSBuffer_t);

    struct  {
        _Bool skipTrustEvaluation;
        _Bool allowAnySignature;
        _Bool allowUnrestrictedLocalSigning;
        _Bool allowInternalCAs;
        _Bool enforceCoreTrust;
        _Bool relaxRestrictedModePerms;
        _Bool relaxProfileTrust;
    } exemptions;
};
typedef struct _CSConfig CSConfig_t;


struct _CSCodeDirectory {
    uint32_t magic;
    uint32_t length;
    uint32_t version;
    uint32_t flags;
    uint32_t hashesOffset;
    uint32_t signingIdentifierOffset;
    uint32_t numSpecialSlots;
    uint32_t numCodeSlots;
    uint32_t codeLimit;
    uint8_t hashSize;
    uint8_t hashType;
    uint8_t platformIdentifier;
    uint8_t pageShift;
    uint32_t spare0;
};

typedef struct _CSCodeDirectory CSCodeDirectory_t;

struct _CSCodeDirectorySafe {
    const CSCodeDirectory_t* data;
    uint32_t dataSize;
};
typedef struct _CSCodeDirectorySafe CSCodeDirectorySafe_t;

struct _CSSuperBlobIndex {
    uint32_t type;
    uint32_t offset;
};
typedef struct _CSSuperBlobIndex CSSuperBlobIndex_t;

struct _CSSuperBlob {
    uint32_t magic;
    uint32_t length;
    uint32_t count;
    CSSuperBlobIndex_t index[0];
};
typedef struct _CSSuperBlob CSSuperBlob_t;

struct _CSSuperBlobSafe {
    const CSSuperBlob_t* data;
    uint32_t dataSize;
};
typedef struct _CSSuperBlobSafe CSSuperBlobSafe_t;

typedef uint8_t CSTrust_t;
struct _CSProfileProperties {
    uint32_t developer : 1;
    uint32_t testFlight : 1;
    uint32_t universal : 1;
    uint32_t appleInternal : 1;
    uint32_t demoMode : 1;
    uint32_t appShack : 1;
    uint32_t internalBuild : 1;
    uint32_t noExecute : 1;
    uint32_t reserved : 23;
};
typedef struct _CSProfileProperties CSProfileProperties_t;
typedef CEContext_t ProfileContext_t;
typedef uint32_t CT_uint32_t;
typedef CT_uint32_t CoreTrustDigestType;

typedef CoreTrustDigestType CMSDigestType_t;

struct _CMSValidation {
    const uint8_t* cmsData;
    size_t cmsDataSize;
    const uint8_t* cmsLeafCert;
    size_t cmsLeafCertSize;
    const uint8_t* cmsContent;
    size_t cmsContentSize;
    CMSDigestType_t agilityHashType;
    const uint8_t* agilityHash;
    size_t agilityHashSize;
    CMSDigestType_t digestType;
    CMSPolicyFlags_t policyFlags;
    _Bool cmsInitialized;
    _Bool cmsVerified;
    _Bool allowDebuggingRoots;
};
typedef struct _CMSValidation CMSValidation_t;
struct _ProfileValidation {
    const CSConfig_t* config;
    CMSValidation_t profileCMS;
    ProfileContext_t profileCtx;
    EntitlementsContext_t entCtx;
    _Bool entInit;
    CSProfileProperties_t properties;
    _Bool profileInitialized;
    _Bool profileVerified;
    _Bool profileTrusted;
};
typedef struct _ProfileValidation ProfileValidation_t;

struct _SignatureValidation {
    const CSConfig_t* config;
    CSBuffer_t signatureBlob;
    CSSuperBlobSafe_t superBlob;
    _Bool unusedBufferAllocated;
    _Bool signatureParsed;
    _Bool appContainerPath;
    CSCodeDirectorySafe_t codeDirectory;
    uint8_t CDHash[20];
    EntitlementsContext_t entCtx;
    _Bool entInit;
    CSTrust_t trustLevelInterim;
    CSTrust_t trustLevel;
    const ProfileValidation_t* profile;
    CSBuffer_t leafCert;
};



int main(int argc, const char* argv[])
{
    struct _CSConfigCallerSignature sig = {};
    return 0;
}
