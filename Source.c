// Excel-o-meter Data Converter
//Adam Carlson

#include <stdio.h>

#define TRUE	1
#define FALSE	0

int sensorCheck(__int16 x){
	__int16 sensorMask = 0x000F;
	return (x & sensorMask); 
}

/*
int dataCheck(__int16 * data){
	__int16 comp = 0x8080;
	if ((data[0] == comp) || (data[1] == comp) || (data[2] == comp))
	{
		return 0;
	}
	return 1;
}
*/

void outputToScreen(float * data, int sensor){
	printf("\nSensor %i:\nxCord: %f\nyCord: %f\nzCord: %f\n", sensor, data[0], data[1], data[2]);
}


__int16 byteSwap(__int16 data){
	return(((data >> 8) & 0x00FF) | ((data << 8) & 0xFF00));
}
/*

int dupCheck(__int16 *oldData, __int16 *newData){
	if ((oldData[0] & 0x00FF) == (newData[0] & 0x00FF)) //&& (oldData[1] == newData[1]) && (oldData[2] == newData[2]))
		return TRUE;
	return FALSE;
}
*/

int main(int argc, char *argv[]){
	
	//__int16 xData = 0;
	//__int16 yData = 0;
	//__int16 zData = 0;

	//int TEMP = 0;

	//__int16 buffer = 0;
	__int16 *dataPoint = (__int16 *)malloc(6);
	//__int16 *oldDP;
	//oldDP = (__int16 *)malloc(6);
	//__int16 *bufPtr;
	float newData[3];
	__int8 info[16];

	int sensor;
	
	FILE *inputFile;
	FILE *s0;
	FILE *s1;
	FILE *s2;
	FILE *outputFile;

	fopen_s(&inputFile, argv[1], "rb");
	fread_s(info, 16, 1, 16, inputFile);
	__int8 numSensors = info[0];
	fprintf(stdout, "%i", numSensors);

	if (numSensors > 0)
		fopen_s(&s0, "s0.dat", "wb");
	if (numSensors > 1)
		fopen_s(&s1, "s1.dat", "wb");
	if (numSensors > 2)
		fopen_s(&s2, "s2.dat", "wb");

	while (fread_s(info, 16, 1, 16, inputFile))
	{
		sensor = info[0];

		if (sensor == 0)
			outputFile = s0;
		else if (sensor == 1)
			outputFile = s1;
		else if (sensor == 2)
			outputFile = s2;


		for (int i = 0; i < 32; i++)
		{
			fread_s(dataPoint, 6, 2, 3, inputFile);
			
			for (int i = 0; i < 3; i++)
			{
				dataPoint[i] = byteSwap(dataPoint[i]);
			}

			// convert to g's
			newData[0] = ((float)(dataPoint[0] >> 2)) / 1024.0;
			newData[1] = ((float)(dataPoint[1] >> 2)) / 1024.0;
			newData[2] = ((float)(dataPoint[2] >> 2)) / 1024.0;

			if (info[1] == 0x00)
				fwrite(newData, sizeof(float), 3, outputFile);
		}
	}
		/*
		// For TEST data:
		dataPoint[0] = dataPoint[0] >> 4;
		dataPoint[1] = dataPoint[1] >> 4;
		dataPoint[2] = dataPoint[2] >> 4;

		newData[0] = (float)dataPoint[0];
		newData[1] = (float)dataPoint[1];
		newData[2] = (float)dataPoint[2];
		*/

	/*
	while (fread_s(dataPoint, 6, 2, 3, inputFile)){
		if (TEMP++, TEMP < 20) continue;
		if (dataCheck(dataPoint)){
			//for (int i = 0; i < 3; i++){
			//	dataPoint[i] = byteSwap(dataPoint[i]);
			//}
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
	*/

	fclose(inputFile);
	if (numSensors > 0)
		fclose(s0);
	if (numSensors > 1)
		fclose(s1);
	if (numSensors > 2)
		fclose(s2);
}