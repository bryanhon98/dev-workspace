package com.example.parcel;

public class RouteEngine {
    public DispatchResult execute(ShipmentEvent event, DispatchAction action) {
        return DispatchResult.accepted(event, action);
    }
}
