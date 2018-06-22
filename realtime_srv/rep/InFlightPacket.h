class NetworkMgr;
class DeliveryNotifyMgr;
class ReplicationMgr;

class InFlightPacket
{
public:
	InFlightPacket( PacketSN inSequenceNumber, ReplicationMgr* inRepMgr, 
		NetworkMgr* inNetworkMgr );
	
	PacketSN GetSequenceNumber() const	{ return mSequenceNumber; }
	float GetTimeDispatched() const	{ return mTimeDispatched; }
	NetworkMgr* getNetworkMgr() const{ return NetworkMgr_; }
public:

	class ReplicationTransmission
	{
	public:
		ReplicationTransmission( int inNetworkId, ReplicationAction inAction, uint32_t inState ) :
			mNetworkId( inNetworkId ),
			mAction( inAction ),
			mState( inState )
		{}

		int							GetNetworkId()		const { return mNetworkId; }
		ReplicationAction			GetAction()			const { return mAction; }
		uint32_t					GetState()			const { return mState; }

	private:
		int							mNetworkId;
		ReplicationAction			mAction;
		uint32_t					mState;
	};

	void AddTransmission( int inNetworkId, ReplicationAction inAction, uint32_t inState );

	virtual void HandleDeliveryFailure( DeliveryNotifyMgr* inDeliveryNotificationManager ) const;
	virtual void HandleDeliverySuccess( DeliveryNotifyMgr* inDeliveryNotificationManager ) const;


private:

	void HandleCreateDeliveryFailure( int inNetworkId ) const;
	void HandleUpdateStateDeliveryFailure( int inNetworkId, uint32_t inState, DeliveryNotifyMgr* inDeliveryNotificationManager ) const;
	void HandleDestroyDeliveryFailure( int inNetworkId ) const;
	void HandleCreateDeliverySuccess( int inNetworkId ) const;
	void HandleDestroyDeliverySuccess( int inNetworkId ) const;

	ReplicationMgr*	mReplicationManager;

	vector< ReplicationTransmission >		mTransmissions;

private:
	PacketSN	mSequenceNumber;
	float		mTimeDispatched;
	NetworkMgr* NetworkMgr_;
};