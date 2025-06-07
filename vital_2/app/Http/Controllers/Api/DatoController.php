<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\Dato;
use App\Events\SensorDataUpdated;


class DatoController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        // Obtener los últimos 15 registros para los gráficos
        $data = Dato::latest()->take(15)->get()->map(function ($item) {
            return [
                'heart_rate' => $item->BPM,
                'temperature' => $item->TEMP,
                'oxygen_level' => $item->SPO2,
                'created_at' => $item->created_at->toDateTimeString()
            ];
        });

        return response()->json(['data' => $data]);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $dato = Dato::create($request->all());

        // Emitir evento para Pusher
        SensorDataUpdated::dispatch($dato);


        return response()->json(['message' => 'Datos guardados']);
    }

    /**
     * Display the specified resource.
     */
    public function show(Dato $dato)
    {
        return $dato;
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, Dato $dato)
    {
        $dato->update($request->all());
        return response()->json($dato, 200);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Dato $dato)
    {
        $dato->delete();
        return response()->json(null, 204);
    }
}
