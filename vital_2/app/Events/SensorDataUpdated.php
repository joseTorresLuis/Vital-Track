<?php

namespace App\Events;

use Illuminate\Broadcasting\Channel;
use Illuminate\Contracts\Broadcasting\ShouldBroadcast;
use Illuminate\Queue\SerializesModels;
use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Broadcasting\InteractsWithSockets;
use Illuminate\Support\Facades\Log;
use App\Models\Dato;

class SensorDataUpdated implements ShouldBroadcast
{
    use Dispatchable, InteractsWithSockets, SerializesModels;

    public $data;

    public function __construct(Dato $dato)
    {
        $this->data = [
            'BPM' => $dato->BPM,
            'SPO2' => $dato->SPO2,
            'TEMP' => $dato->TEMP,
            'created_at' => $dato->created_at->toDateTimeString()
        ];

        Log::info('Evento SensorDataUpdated emitido', ['data' => $this->data]);
    }

    public function broadcastOn()
    {
        return new Channel('sensor-data'); // Debe coincidir con Echo.channel('sensor-data')
    }

    public function broadcastAs()
    {
        return 'SensorDataUpdated'; // Debe coincidir con .listen('SensorDataUpdated')
    }
}
