<?php

use App\Http\Controllers\Api\DatoController;
use Illuminate\Support\Facades\Route;

Route::apiResource('datos', DatoController::class);
Route::get('/sensor-data', [DatoController::class, 'index']);
