/*
 * Copyright (c) 2025 Huawei Device Co., Ltd.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

const lib = requireNapi('./typedarray_test.so', RequireBaseDir.SCRIPT_DIR);

function main() {
  let u8arr = lib.NewUint8Array(5, 10);
  if ( u8arr[0] !== 10) throw new Error(`Unexpected result`);
  console.log("NewUint8Array:", u8arr.toString());

  let u8sum = lib.SumUint8Array(u8arr);
  if ( u8sum !== 50) throw new Error(`Unexpected result`);
  console.log("SumUint8Array:", u8sum);

  let i8arr = lib.NewInt8Array(5, -10);
  if ( i8arr[0] !== -10) throw new Error(`Unexpected result`);
  console.log("NewInt8Array:", i8arr.toString());

  let i8sum = lib.SumInt8Array(i8arr);
  if ( i8sum !== -50) throw new Error(`Unexpected result`);
  console.log("SumInt8Array:", i8sum);

  let u16arr = lib.NewUint16Array(5, 100);
  if ( u16arr[0] !== 100) throw new Error(`Unexpected result`);
  console.log("NewUint16Array:", u16arr.toString());

  let u16sum = lib.SumUint16Array(u16arr);
  if ( u16sum !== 500) throw new Error(`Unexpected result`);
  console.log("SumUint16Array:", u16sum);

  let i16arr = lib.NewInt16Array(5, -100);
  if ( i16arr[0] !== -100) throw new Error(`Unexpected result`);
  console.log("NewInt16Array:", i16arr.toString());

  let i16sum = lib.SumInt16Array(i16arr);
  if ( i16sum !== -500) throw new Error(`Unexpected result`);
  console.log("SumInt16Array:", i16sum);

  let u32arr = lib.NewUint32Array(5, 1000);
  if ( u32arr[0] !== 1000) throw new Error(`Unexpected result`);
  console.log("NewUint32Array:", u32arr.toString());

  let u32sum = lib.SumUint32Array(u32arr);
  if ( u32sum !== 5000) throw new Error(`Unexpected result`);
  console.log("SumUint32Array:", u32sum);

  let i32arr = lib.NewInt32Array(5, -1000);
  if ( i32arr[0] !== -1000) throw new Error(`Unexpected result`);
  console.log("NewInt32Array:", i32arr.toString());

  let i32sum = lib.SumInt32Array(i32arr);
  if ( i32sum !== -5000) throw new Error(`Unexpected result`);
  console.log("SumInt32Array:", i32sum);

  let u64arr = lib.NewBigUint64Array(5, 10000);
  if ( u64arr[0] !== 10000n) throw new Error(`Unexpected result`);
  console.log("NewBigUint64Array:", u64arr.toString());

  let u64sum = lib.SumBigUint64Array(u64arr);
  if ( u64sum !== 50000) throw new Error(`Unexpected result`);
  console.log("SumBigUint64Array:", u64sum);

  let i64arr = lib.NewBigInt64Array(5, -10000);
  if ( i64arr[0] !== -10000n) throw new Error(`Unexpected result`);
  console.log("NewBigInt64Array:", i64arr.toString());

  let i64sum = lib.SumBigInt64Array(i64arr);
  if ( i64sum !== -50000) throw new Error(`Unexpected result`);
  console.log("SumBigInt64Array:", i64sum);

  const EPSILON = 1e-6;  // 0.000001
  let f32arr = lib.NewFloat32Array(5, 3.14);
  if ( !(Math.abs(f32arr[0] - 3.14) < EPSILON) ) throw new Error(`Unexpected result`);
  console.log("NewFloat32Array:", f32arr.toString());

  let f32sum = lib.SumFloat32Array(f32arr);
  if (!(Math.abs(f32sum - 15.7) < EPSILON)) throw new Error(`Unexpected result`);
  console.log("SumFloat32Array:", f32sum);

  let f64arr = lib.NewFloat64Array(5, 6.28);
  if ( !(Math.abs(f64arr[0] - 6.28) < EPSILON) ) throw new Error(`Unexpected result`);
  console.log("NewFloat64Array:", f64arr.toString());

  let f64sum = lib.SumFloat64Array(f64arr);
  if (!(Math.abs(f64sum - 31.4) < EPSILON)) throw new Error(`Unexpected result`);
  console.log("SumFloat64Array:", f64sum);

  let myinfo = lib.GetTypedArrInfo();

  let newarru8 = new Uint8Array([1, 2, 3]);
  let u8arrres = myinfo.PrintUint8Array(newarru8);
  if( u8arrres[0] !== 1 || u8arrres[1] !== 2 || u8arrres[2] !== 3) throw new Error(`Unexpected result`);
  if( myinfo.Uint8Array[0] !== 1 || myinfo.Uint8Array[1] !== 2 || myinfo.Uint8Array[2] !== 3) throw new Error(`Unexpected result`);

  myinfo.Uint8Array = new Uint8Array([4, 5, 6]);
  if( myinfo.Uint8Array[0] !== 4 || myinfo.Uint8Array[1] !== 5 || myinfo.Uint8Array[2] !== 6) throw new Error(`Unexpected result`);
  myinfo.Uint8Array = new Uint8Array([5, 4, 3]);
  if( myinfo.Uint8Array[0] !== 5 || myinfo.Uint8Array[1] !== 4 || myinfo.Uint8Array[2] !== 3) throw new Error(`Unexpected result`);

  let newarri8 = new Int8Array([-1, -2, -3]);
  let i8arrres = myinfo.PrintInt8Array(newarri8);
  if( i8arrres[0] !== -1 || i8arrres[1] !== -2 || i8arrres[2] !== -3) throw new Error(`Unexpected result`);
  if( myinfo.Int8Array[0] !== -1 || myinfo.Int8Array[1] !== -2 || myinfo.Int8Array[2] !== -3) throw new Error(`Unexpected result`);

  myinfo.Int8Array = new Int8Array([-4, -5, -6]);
  if( myinfo.Int8Array[0] !== -4 || myinfo.Int8Array[1] !== -5 || myinfo.Int8Array[2] !== -6) throw new Error(`Unexpected result`);
  myinfo.Int8Array = new Int8Array([-6, -5, -4]);
  if( myinfo.Int8Array[0] !== -6 || myinfo.Int8Array[1] !== -5 || myinfo.Int8Array[2] !== -4) throw new Error(`Unexpected result`);

  let newarru16 = new Uint16Array([100, 200, 300]);
  let u16arrres = myinfo.PrintUint16Array(newarru16);
  if( u16arrres[0] !== 100 || u16arrres[1] !== 200 || u16arrres[2] !== 300) throw new Error(`Unexpected result`);
  if( myinfo.Uint16Array[0] !== 100 || myinfo.Uint16Array[1] !== 200 || myinfo.Uint16Array[2] !== 300) throw new Error(`Unexpected result`);

  myinfo.Uint16Array = new Uint16Array([400, 500, 600]);
  if( myinfo.Uint16Array[0] !== 400 || myinfo.Uint16Array[1] !== 500 || myinfo.Uint16Array[2] !== 600) throw new Error(`Unexpected result`);
  myinfo.Uint16Array = new Uint16Array([600, 500, 400]);
  if( myinfo.Uint16Array[0] !== 600 || myinfo.Uint16Array[1] !== 500 || myinfo.Uint16Array[2] !== 400) throw new Error(`Unexpected result`);

  let newarri16 = new Int16Array([-100, -200, -300]);
  let i16arrres = myinfo.PrintInt16Array(newarri16);
  if( i16arrres[0] !== -100 || i16arrres[1] !== -200 || i16arrres[2] !== -300) throw new Error(`Unexpected result`);
  if( myinfo.Int16Array[0] !== -100 || myinfo.Int16Array[1] !== -200 || myinfo.Int16Array[2] !== -300) throw new Error(`Unexpected result`);

  myinfo.Int16Array = new Int16Array([-400, -500, -600]);
  if( myinfo.Int16Array[0] !== -400 || myinfo.Int16Array[1] !== -500 || myinfo.Int16Array[2] !== -600) throw new Error(`Unexpected result`);
  myinfo.Int16Array = new Int16Array([-600, -500, -400]);
  if( myinfo.Int16Array[0] !== -600 || myinfo.Int16Array[1] !== -500 || myinfo.Int16Array[2] !== -400) throw new Error(`Unexpected result`);

  let newarru32 = new Uint32Array([1000, 2000, 3000]);
  let u32arrres = myinfo.PrintUint32Array(newarru32);
  if( u32arrres[0] !== 1000 || u32arrres[1] !== 2000 || u32arrres[2] !== 3000) throw new Error(`Unexpected result`);
  if( myinfo.Uint32Array[0] !== 1000 || myinfo.Uint32Array[1] !== 2000 || myinfo.Uint32Array[2] !== 3000) throw new Error(`Unexpected result`);
  
  myinfo.Uint32Array = new Uint32Array([4000, 5000, 6000]);
  if( myinfo.Uint32Array[0] !== 4000 || myinfo.Uint32Array[1] !== 5000 || myinfo.Uint32Array[2] !== 6000) throw new Error(`Unexpected result`);
  myinfo.Uint32Array = new Uint32Array([6000, 5000, 4000]);
  if( myinfo.Uint32Array[0] !== 6000 || myinfo.Uint32Array[1] !== 5000 || myinfo.Uint32Array[2] !== 4000) throw new Error(`Unexpected result`);

  let newarri32 = new Int32Array([-1000, -2000, -3000]);
  let i32arrres = myinfo.PrintInt32Array(newarri32);
  if( i32arrres[0] !== -1000 || i32arrres[1] !== -2000 || i32arrres[2] !== -3000) throw new Error(`Unexpected result`);
  if( myinfo.Int32Array[0] !== -1000 || myinfo.Int32Array[1] !== -2000 || myinfo.Int32Array[2] !== -3000) throw new Error(`Unexpected result`);

  myinfo.Int32Array = new Int32Array([-4000, -5000, -6000]);
  if( myinfo.Int32Array[0] !== -4000 || myinfo.Int32Array[1] !== -5000 || myinfo.Int32Array[2] !== -6000) throw new Error(`Unexpected result`);
  myinfo.Int32Array = new Int32Array([-6000, -5000, -4000]);
  if( myinfo.Int32Array[0] !== -6000 || myinfo.Int32Array[1] !== -5000 || myinfo.Int32Array[2] !== -4000) throw new Error(`Unexpected result`);
  
  let newarru64 = new BigUint64Array([10000n, 20000n, 30000n]);
  let u64arrres = myinfo.PrintUint64Array(newarru64);
  if( u64arrres[0] !== 10000n || u64arrres[1] !== 20000n || u64arrres[2] !== 30000n) throw new Error(`Unexpected result`);
  if( myinfo.Uint64Array[0] !== 10000n || myinfo.Uint64Array[1] !== 20000n || myinfo.Uint64Array[2] !== 30000n) throw new Error(`Unexpected result`);

  myinfo.Uint64Array = new BigUint64Array([40000n, 50000n, 60000n]);
  if( myinfo.Uint64Array[0] !== 40000n || myinfo.Uint64Array[1] !== 50000n || myinfo.Uint64Array[2] !== 60000n) throw new Error(`Unexpected result`);
  myinfo.Uint64Array = new BigUint64Array([60000n, 50000n, 40000n]);
  if( myinfo.Uint64Array[0] !== 60000n || myinfo.Uint64Array[1] !== 50000n || myinfo.Uint64Array[2] !== 40000n) throw new Error(`Unexpected result`);
  
  let newarri64 = new BigInt64Array([-10000n, -20000n, -30000n]);
  let i64arrres = myinfo.PrintInt64Array(newarri64);
  if( i64arrres[0] !== -10000n || i64arrres[1] !== -20000n || i64arrres[2] !== -30000n) throw new Error(`Unexpected result`);
  if( myinfo.Int64Array[0] !== -10000n || myinfo.Int64Array[1] !== -20000n || myinfo.Int64Array[2] !== -30000n) throw new Error(`Unexpected result`);

  myinfo.Int64Array = new BigInt64Array([-40000n, -50000n, -60000n]);
  if( myinfo.Int64Array[0] !== -40000n || myinfo.Int64Array[1] !== -50000n || myinfo.Int64Array[2] !== -60000n) throw new Error(`Unexpected result`);
  myinfo.Int64Array = new BigInt64Array([-60000n, -50000n, -40000n]);
  if( myinfo.Int64Array[0] !== -60000n || myinfo.Int64Array[1] !== -50000n || myinfo.Int64Array[2] !== -40000n) throw new Error(`Unexpected result`);

  let newarrf32 = new Float32Array([1.1, 2.2, 3.3]);
  let f32arrres = myinfo.PrintFloat32Array(newarrf32);
  if( !(Math.abs(f32arrres[0] - 1.1) < EPSILON) || !(Math.abs(f32arrres[1] - 2.2) < EPSILON) || !(Math.abs(f32arrres[2] - 3.3) < EPSILON) ) throw new Error(`Unexpected result`);
  if( !(Math.abs(myinfo.Float32Array[0] - 1.1) < EPSILON) || !(Math.abs(myinfo.Float32Array[1] - 2.2) < EPSILON) || !(Math.abs(myinfo.Float32Array[2] - 3.3) < EPSILON) ) throw new Error(`Unexpected result`);

  myinfo.Float32Array = new Float32Array([4.4, 5.5, 6.6]);
  if( !(Math.abs(myinfo.Float32Array[0] - 4.4) < EPSILON) || !(Math.abs(myinfo.Float32Array[1] - 5.5) < EPSILON) || !(Math.abs(myinfo.Float32Array[2] - 6.6) < EPSILON) ) throw new Error(`Unexpected result`);
  myinfo.Float32Array = new Float32Array([6.6, 5.5, 4.4]);
  if( !(Math.abs(myinfo.Float32Array[0] - 6.6) < EPSILON) || !(Math.abs(myinfo.Float32Array[1] - 5.5) < EPSILON) || !(Math.abs(myinfo.Float32Array[2] - 4.4) < EPSILON) ) throw new Error(`Unexpected result`);
  
  let newarrf64 = new Float64Array([7.7, 8.8, 9.9]);
  let f64arrres = myinfo.PrintFloat64Array(newarrf64);
  if( !(Math.abs(f64arrres[0] - 7.7) < EPSILON) || !(Math.abs(f64arrres[1] - 8.8) < EPSILON) || !(Math.abs(f64arrres[2] - 9.9) < EPSILON) ) throw new Error(`Unexpected result`);
  if( !(Math.abs(myinfo.Float64Array[0] - 7.7) < EPSILON) || !(Math.abs(myinfo.Float64Array[1] - 8.8) < EPSILON) || !(Math.abs(myinfo.Float64Array[2] - 9.9) < EPSILON) ) throw new Error(`Unexpected result`);

  myinfo.Float64Array = new Float64Array([10.1, 11.11, 12.12]);
  if( !(Math.abs(myinfo.Float64Array[0] - 10.1) < EPSILON) || !(Math.abs(myinfo.Float64Array[1] - 11.11) < EPSILON) || !(Math.abs(myinfo.Float64Array[2] - 12.12) < EPSILON) ) throw new Error(`Unexpected result`);
  myinfo.Float64Array = new Float64Array([12.12, 11.11, 10.1]);
  if( !(Math.abs(myinfo.Float64Array[0] - 12.12) < EPSILON) || !(Math.abs(myinfo.Float64Array[1] - 11.11) < EPSILON) || !(Math.abs(myinfo.Float64Array[2] - 10.1) < EPSILON) ) throw new Error(`Unexpected result`);

  let optu8arrres = myinfo.GetUint8ArrayOptional(newarru8);
  if( optu8arrres[0] !== 1 || optu8arrres[1] !== 2 || optu8arrres[2] !== 3) throw new Error(`Unexpected result`);
  let optu8arrres2 = myinfo.GetUint8ArrayOptional(undefined);
  if( optu8arrres2.length !== 0 ) throw new Error(`Unexpected result`);

  let opti8arrres = myinfo.GetInt8ArrayOptional(newarri8);
  if( opti8arrres[0] !== -1 || opti8arrres[1] !== -2 || opti8arrres[2] !== -3) throw new Error(`Unexpected result`);
  let opti8arrres2 = myinfo.GetInt8ArrayOptional(undefined);
  if( opti8arrres2.length !== 0 ) throw new Error(`Unexpected result`);

  let  optu16arrres = myinfo.GetUint16ArrayOptional(newarru16);
  if( optu16arrres[0] !== 100 || optu16arrres[1] !== 200 || optu16arrres[2] !== 300) throw new Error(`Unexpected result`);
  let  optu16arrres2 = myinfo.GetUint16ArrayOptional(undefined);
  if( optu16arrres2.length !== 0 ) throw new Error(`Unexpected result`);
  
  let opti16arrres = myinfo.GetInt16ArrayOptional(newarri16);
  if( opti16arrres[0] !== -100 || opti16arrres[1] !== -200 || opti16arrres[2] !== -300) throw new Error(`Unexpected result`);
  let opti16arrres2 = myinfo.GetInt16ArrayOptional(undefined);
  if( opti16arrres2.length !== 0 ) throw new Error(`Unexpected result`);

  let optu32arrres = myinfo.GetUint32ArrayOptional(newarru32);
  if( optu32arrres[0] !== 1000 || optu32arrres[1] !== 2000 || optu32arrres[2] !== 3000) throw new Error(`Unexpected result`);
  let optu32arrres2 = myinfo.GetUint32ArrayOptional(undefined);
  if( optu32arrres2.length !== 0 ) throw new Error(`Unexpected result`);

  let opti32arrres = myinfo.GetInt32ArrayOptional(newarri32);
  if( opti32arrres[0] !== -1000 || opti32arrres[1] !== -2000 || opti32arrres[2] !== -3000) throw new Error(`Unexpected result`);
  let opti32arrres2 = myinfo.GetInt32ArrayOptional(undefined);
  if( opti32arrres2.length !== 0 ) throw new Error(`Unexpected result`);

  let optu64arrres = myinfo.GetUint64ArrayOptional(newarru64);
  if( optu64arrres[0] !== 10000 || optu64arrres[1] !== 20000 || optu64arrres[2] !== 30000) throw new Error(`Unexpected result`);
  let optu64arrres2 = myinfo.GetUint64ArrayOptional(undefined);
  if( optu64arrres2.length !== 0 ) throw new Error(`Unexpected result`);

  let opti64arrres = myinfo.GetInt64ArrayOptional(newarri64);
  if( opti64arrres[0] !== -10000 || opti64arrres[1] !== -20000 || opti64arrres[2] !== -30000) throw new Error(`Unexpected result`);
  let opti64arrres2 = myinfo.GetInt64ArrayOptional(undefined);
  if( opti64arrres2.length !== 0 ) throw new Error(`Unexpected result`);

  let optf32arrres = myinfo.GetFloat32ArrayOptional(newarrf32);
  if( optf32arrres[0] !== 1 || optf32arrres[1] !== 2 || optf32arrres[2] !== 3) throw new Error(`Unexpected result`);
  let optf32arrres2 = myinfo.GetFloat32ArrayOptional(undefined);
  if( optf32arrres2.length !== 0 ) throw new Error(`Unexpected result`);

  let optf64arrres = myinfo.GetFloat64ArrayOptional(newarrf64);
  if( optf64arrres[0] !== 7 || optf64arrres[1] !== 8 || optf64arrres[2] !== 9) throw new Error(`Unexpected result`);
  let optf64arrres2 = myinfo.GetFloat64ArrayOptional(undefined);
  if( optf64arrres2.length !== 0 ) throw new Error(`Unexpected result`);

  let recarru8: Record<string, Uint8Array> = {
      "uint8Key": newarru8,
  };
  let recrecarru8res = myinfo.MapUint8Arrays(recarru8);
  if ( recrecarru8res["uint8Key"][0] !== 1 || recrecarru8res["uint8Key"][1] !== 2 || recrecarru8res["uint8Key"][2] !== 3) throw new Error(`Unexpected result`);

  let recarri8: Record<string, Int8Array> = {
      "int8Key": newarri8,
  };
  let recrecarri8res = myinfo.MapInt8Arrays(recarri8);
  if ( recrecarri8res["int8Key"][0] !== -1 || recrecarri8res["int8Key"][1] !== -2 || recrecarri8res["int8Key"][2] !== -3) throw new Error(`Unexpected result`);

  let recarru16: Record<string, Uint16Array> = {
      "uint16Key": newarru16,
  };
  let recrecarru16res = myinfo.MapUint16Arrays(recarru16);
  if ( recrecarru16res["uint16Key"][0] !== 100 || recrecarru16res["uint16Key"][1] !== 200 || recrecarru16res["uint16Key"][2] !== 300) throw new Error(`Unexpected result`);
  
  let recarri16: Record<string, Int16Array> = {
      "int16Key": newarri16,
  };
  let recrecarri16res = myinfo.MapInt16Arrays(recarri16);
  if ( recrecarri16res["int16Key"][0] !== -100 || recrecarri16res["int16Key"][1] !== -200 || recrecarri16res["int16Key"][2] !== -300) throw new Error(`Unexpected result`);

  let recarru32: Record<string, Uint32Array> = {
      "uint32Key": newarru32,
  };
  let recrecarru32res = myinfo.MapUint32Arrays(recarru32);
  if ( recrecarru32res["uint32Key"][0] !== 1000 || recrecarru32res["uint32Key"][1] !== 2000 || recrecarru32res["uint32Key"][2] !== 3000) throw new Error(`Unexpected result`);
  
  let recarri32: Record<string, Int32Array> = {
      "int32Key": newarri32,
  };
  let recrecarri32res = myinfo.MapInt32Arrays(recarri32);
  if ( recrecarri32res["int32Key"][0] !== -1000 || recrecarri32res["int32Key"][1] !== -2000 || recrecarri32res["int32Key"][2] !== -3000) throw new Error(`Unexpected result`);

  let recarru64: Record<string, BigUint64Array> = {
      "uint64Key": newarru64,
  };
  let recrecarru64res = myinfo.MapUint64Arrays(recarru64);
  if ( recrecarru64res["uint64Key"][0] !== 10000n || recrecarru64res["uint64Key"][1] !== 20000n || recrecarru64res["uint64Key"][2] !== 30000n) throw new Error(`Unexpected result`);
  
  let recarri64: Record<string, BigInt64Array> = {
      "int64Key": newarri64,
  };
  let recrecarri64res = myinfo.MapInt64Arrays(recarri64);
  if ( recrecarri64res["int64Key"][0] !== -10000n || recrecarri64res["int64Key"][1] !== -20000n || recrecarri64res["int64Key"][2] !== -30000n) throw new Error(`Unexpected result`);

  let recarrf32: Record<string, Float32Array> = {
      "float32Key": newarrf32,
  };
  let recrecarrf32res = myinfo.MapFloat32Arrays(recarrf32);
  if ( !(Math.abs(recrecarrf32res["float32Key"][0] - 1.1) < EPSILON) || !(Math.abs(recrecarrf32res["float32Key"][1] - 2.2) < EPSILON) || !(Math.abs(recrecarrf32res["float32Key"][2] - 3.3) < EPSILON) ) throw new Error(`Unexpected result`);
  
  let recarrf64: Record<string, Float64Array> = {
      "float64Key": newarrf64,
  };
  let recrecarrf64res = myinfo.MapFloat64Arrays(recarrf64);
  if ( !(Math.abs(recrecarrf64res["float64Key"][0] - 7.7) < EPSILON) || !(Math.abs(recrecarrf64res["float64Key"][1] - 8.8) < EPSILON) || !(Math.abs(recrecarrf64res["float64Key"][2] - 9.9) < EPSILON) ) throw new Error(`Unexpected result`);

  let mystruct = {
    a: newarru8,
    b: newarri8,
    c: newarru16,
    d: newarri16,
    e: newarru32,
    f: newarri32,
    g: newarru64,
    h: newarri64,
    i: newarrf32,
    j: newarrf64
  }
  let structres = lib.SetupStructAndPrint(mystruct);
  if( structres.a[0] !== 1 || structres.b[0] !== -1 || structres.c[0] !== 100 || structres.d[0] !== -100 ||
      structres.e[0] !== 1000 || structres.f[0] !== -1000 || structres.g[0] !== 10000n || structres.h[0] !== -10000n ||
      !(Math.abs(structres.i[0] - 1.1) < EPSILON) || !(Math.abs(structres.j[0] - 7.7) < EPSILON) ) throw new Error(`Unexpected result`);
  
  console.log("All TypedArray tests passed.");
}

main();
