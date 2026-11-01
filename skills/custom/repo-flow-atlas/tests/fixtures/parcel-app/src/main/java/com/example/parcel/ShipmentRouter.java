package com.example.parcel;

public class ShipmentRouter {
    private RouteEngine engine;

    public DispatchResult route(ShipmentEvent event) {
        Log.info("received", 
            Json.stringify(event));
        Checks.require(event != null, Error.INVALID_EVENT);
        if (event.kind() == EventKind.CREATED) {
            return engine.execute(event, DispatchAction.CREATE_LABEL);
        }
        return engine.execute(event, DispatchAction.UPDATE_TRACKING);
    }
}
