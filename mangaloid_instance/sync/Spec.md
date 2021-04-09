# Chuck's Protocol

## API Routes

- __GET `/sync/subscribe` ? address__   
Sent by another instance that wants to subscribe to this instance.

- __GET `/sync/accept` ? address__
Sent by  another instance to which we have requested subscription, for verification purposes.

- __POST `/sync/push` : JSON Body__
Sent by another instance to which we have subscribed, to notify us of a database modification.

## Sync Body

```json
{
    "action" : "CREATE / MODIFY / DELETE",
    "item_type" : "Manga / Chapter",
    "instance" : "The Instance address that sent this push",
    "payload" : "JSON of item_type object, encrypted with the public key corresponding to instance and encoded in Base64"
}
```

## Implementation

### Subscribing
Let's consider the following scenario, where __Instance 1 (i1.mangaloid.moe)__ wants to subscribe to __Instance 2 (i2.mangaloid.moe)__. These are the requests that will be sent:

1) Instance 1 -> `i2.mangaloid.moe/subscribe/?address=i1.mangaloid.moe`
2) Instance 2 -> `i1.mangaloid.moe/accept/?address=i2.mangaloid.moe`

The result of __Request 1__ depends on the result of __Request 2__ and can be one of the following:
- __201:__ `{"message" : "OK"}`
- __403:__ `{"message" : "The instance did not accept our subscription: 'messsage'"}`
- __400:__ `{"message" : "Could not connect to the instance"}`

The result of __Request 2__ can be one of the following:
- __200:__ `{ ...Instance Object..., "public_key" : "PEM" }`
- __403:__ `{"message" : "Not expecting subscription from this address"}`

If both requests return 2XX and everything went fine __Instance 1__ should be subscribed to __Instance 2__. From this point on __Instance 2__ should start sending `/sync/push` reequests to __Instance 1__ on every database update (See __Sync Body__ above), where `payload` should be encrypted with the public_key __Instance 2__ received during __Request 2__.  
   
Instances should use different public-private key pairs for each subscription. That way, if __Instance 2__ for example, is compromised and the public key leaks, we can invalidate only said key, and continue to receive push requests from other instances normally.

### Unsubscribing
There is no "special" unsubscribe method. On the next sync event, simply return __403__. From that point on __Instance 2__ should not attempt to send any more push requests unless another subscription occurs.