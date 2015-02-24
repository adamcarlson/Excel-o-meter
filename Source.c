// Excel-o-meter Data Converter
//Adam Carlson

#include <stdio.h>
#include <Windows.h>

int sensorCheck(__int16 x){
	__int16 sensorMask = 0x03;
	return (x & sensorMask);
}

int dataCheck(__int16 * data){
	__int16 comp = 0x8080;
	if ((data[0] == comp) || (data[1] == comp) || (data[2] == comp))
	{
		return 0;
	}
	return 1;
}

void outputToScreen(float * data){
	printf("xCord: %f\nyCord: %f\nzCord: %f\n\n%i\n\n", data[0], data[1], data[2], sizeof(__int16));
}

__int16 byteSwap(__int16 data){
	return(((data >> 8) & 0x00FF) | ((data << 8) & 0xFF00));
}

BOOL dupCheck(__int16 *oldData, __int16 *newData){
	if ((oldData[0] == newData[0]) && (oldData[1] == newData[1]) && (oldData[2] == newData[2]))
		return TRUE;
	return FALSE;
}

int main(int argc, char *argv[]){
	
	__int16 xData = 0;
	__int16 yData = 0;
	__int16 zData = 0;

	__int16 buffer = 0;
	__int16 *dataPoint;
	dataPoint = (__int16 *)malloc(3);
	__int16 *oldDP;
	oldDP = (__int16 *)malloc(3);
	__int16 *bufPtr;
	float newData[3];

	int sensor = 0;
	
	FILE *inputFile;
	FILE *s1;
	FILE *s2;
	FILE *s3;
	FILE *outputFile;

	inputFile = fopen(argv[1], "rb");
	s1 = fopen("s1.dat", "wb");
	s2 = fopen("test.dat", "wb");

	while (fread_s(dataPoint, 6, 2, 3, inputFile)){
		if (dataCheck(dataPoint)){
			for (int i = 0; i < 3; i++){
				dataPoint[i] = byteSwap(dataPoint[i]);
			}
			if (!dupCheck(oldDP, dataPoint)){
				fwrite(dataPoint, sizeof(__int16), 3, s2);
				sensor = sensorCheck(dataPoint[0]);
				newData[0] = ((float)(dataPoint[0] >> 2)) / 1024.0;
				newData[1] = ((float)(dataPoint[1] >> 2)) / 1024.0;
				newData[2] = ((float)(dataPoint[2] >> 2)) / 1024.0;

				outputToScreen(newData);

				if (sensor == 1)
					outputFile = s1;
				else if (sensor == 2)
					outputFile = s1;
				else
					outputFile = s1;

				fwrite(newData, sizeof(float), 3, outputFile);
				bufPtr = dataPoint;
				dataPoint = oldDP;
				oldDP = bufPtr;
			}
		}
	}

	fclose(inputFile);
	fclose(s1);
}