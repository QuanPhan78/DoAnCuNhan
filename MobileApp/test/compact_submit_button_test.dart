import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:quan_ly_cho_thue_thiet_bi/widgets/core/custom_button.dart';

void main() {
  testWidgets('confirmation button wraps beside its progress indicator on a phone', (tester) async {
    await tester.pumpWidget(MaterialApp(home:Scaffold(body:Align(alignment:Alignment.topLeft,
      child:SizedBox(width:330,child:Row(children:[
        Expanded(child:CustomButton(text:'QUAY LẠI',onPressed:(){})),
        const SizedBox(width:16),
        Expanded(child:CustomButton(text:'XÁC NHẬN THUÊ',isLoading:true,onPressed:(){})),
      ]))))));
    expect(tester.takeException(),isNull);
    expect(find.text('XÁC NHẬN THUÊ'),findsOneWidget);
  });
}
