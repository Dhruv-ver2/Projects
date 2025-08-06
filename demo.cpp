#include<iostream>
#include<climits>
using namespace std;

int main() {

    int arr[]={4,1,5,2,3};
    int n=sizeof(arr)/sizeof(arr[0]);

    for(int i=0; i<n-1; i++) {
        int si=i;
        int mine=INT_MAX;
        for(int j=i+1; j<n; j++) {
            if(arr[j]<arr[si]){
                si=j;
            }
        }

        swap(arr[i],arr[si]);
    }

    cout<<"Sorted array: ";
    for(int i=0; i<n; i++) {
        cout<<arr[i]<<" ";
    }
    return 0;
}